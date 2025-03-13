const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const fs = require('fs-extra');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const PORT = 3000;
const sharedFolder = path.join(__dirname, 'shared');

// 공유 폴더 생성
fs.ensureDirSync(sharedFolder);

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
    console.log('A user connected');

    socket.on('request-files', () => {
        fs.readdir(sharedFolder, (err, files) => {
            if (err) {
                socket.emit('file-list', { success: false, msg: 'Failed to read directory' });
            } else {
                socket.emit('file-list', { success: true, files });
            }
        });
    });

    socket.on('request-file', (fileName) => {
        const filePath = path.join(sharedFolder, fileName);
        fs.readFile(filePath, (err, data) => {
            if (err) {
                socket.emit('file-data', { success: false, msg: 'Failed to read file' });
            } else {
                socket.emit('file-data', { success: true, fileName, data });
            }
        });
    });
});

server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
