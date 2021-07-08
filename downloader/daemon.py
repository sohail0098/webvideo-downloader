# -*- coding:utf-8 -*-
import json
import threading
import queue
from dispatcher import TaskDispatcher
import config
import tools
from tools import WebServer, CLIENT_CLOSE_EXCEPTION


# Background server in daemon mode
class DownloadServer(WebServer):
    ESTABLISHED = 0
    IN_TRANSIT = 1
    DATA_CACHE_SIZE = 10

    # Task queue : waiting for download
    taskQueue = queue.Queue()


    # Handle http requests
    def do_POST(self, client):
        try:
            body = client.rfile.read(int(client.headers['Content-Length']))
            task = json.loads(body.decode('utf-8'))
            self.printWithoutData(task)
            self.taskQueue.put(task)
            tools.normalResponse(client, "success")
        except Exception as e:
            tools.normalResponse(client, "failed")

    def new_client(self, client):
        client.status = self.ESTABLISHED

    # Handling websocket requests
    def message_received(self, client, msg):
        try:
            if client.status == self.ESTABLISHED:
                task = json.loads(msg.decode('utf-8'))
                self.taskQueue.put(task)
                client.task = task
                self.printWithoutData(task)

                if task['type'] == 'stream':
                    client.status = self.IN_TRANSIT
                    task['close'] = lambda : self.close(client)
                    task['dataQueue'] = queue.Queue(self.DATA_CACHE_SIZE)
                    for i in range(self.DATA_CACHE_SIZE):
                        task['dataQueue'].put(None)

            elif client.status == self.IN_TRANSIT:
                desc, chunk = msg.split(b'\r\n', 1)
                data = json.loads(desc.decode('utf-8'))
                data['chunk'] = chunk
                client.task['dataQueue'].put(data)

            self.send_message(client, 'success')
        except:
            self.send_message(client, 'failed')

    def client_left(self, client):
        if client.task and client.task.get('type') == 'stream':
            client.task['dataQueue'].put(CLIENT_CLOSE_EXCEPTION)

    def printWithoutData(self, task):
        copyTask = {key: task[key] for key in task}
        if copyTask.get('data'):
            copyTask['data'] = '...'
        print('\nReceive: %s\n' % tools.stringify(copyTask))


class Runner:
    def __init__(self):
        self.taskDispatcher = TaskDispatcher()

    def start(self):
        if config.interactive:
            self.startInteractive()
        else:
            self.startDaemon(config.port)

    # Interactive mode, accepts user input
    def startInteractive(self):
        while True:
            try:
                url = input('Enter m3u8 link or local path to m3u8 file: ').strip()
                fileName = input('Input file name: ').strip()
                isMultiPart = url.find('www.bilibili.com') != -1
                pRange = input('Enter the first and last Part (space separated) or single Part: ').strip() if isMultiPart else None
            except KeyboardInterrupt:
                break

            self.taskDispatcher.dispatch(url=url, fileName=fileName, pRange=pRange)

    # Daemon mode, monitoring web requests
    def startDaemon(self, port):
        t = threading.Thread(target=self._downloadThread, daemon=True)
        t.start()

        server = DownloadServer(port)

        while True:
            try:
                print("Listening on port %d for clients..." % port)
                server.serve_forever()
            except KeyboardInterrupt:
                if self.taskDispatcher.task:
                    self.taskDispatcher.shutdown()
                else:
                    break

    def _downloadThread(self):
        while True:
            task = DownloadServer.taskQueue.get()
            print('Handle: "%s"' % task['fileName'])
            self.taskDispatcher.dispatch(**task)



if __name__ == '__main__':
    runner = Runner()
    runner.start()
