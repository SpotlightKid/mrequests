// Run this with:
//
//    node server-chunked-response.js
//
// and let your tests make requests to http://localhost:1337/
//
var http = require('http');

http.createServer(function (request, response) {
    response.setHeader('Content-Type', 'text/html; charset=UTF-8');
    response.setHeader('Transfer-Encoding', 'chunked');

    var html =
        '<!DOCTYPE html>\n' +
        '<html lang="en">\n' +
        '<head>\n' +
        '<meta charset="utf-8">\n' +
        '<title>Chunked transfer encoding test</title>\n' +
        '</head>\n' +
        '<body>\n';
    response.write(html);

    html = '<h1>Chunked transfer encoding test</h1>\n'
    response.write(html);

    // Now imitate a long request which lasts 5 seconds.
    setTimeout(function(){
        html =
            '<p>This is a chunked response after 5 seconds. ' +
            'The server should not close the stream before all chunks are sent to a client.</p>\n';
        response.write(html);

        // since this is the last chunk, close the stream.
        html = '</body></html>\n';
        response.end(html);
    }, 5000);

    // this is another chunk of data sent to a client after 2 seconds before the
    // 5-second chunk is sent.
    setTimeout(function(){
        html =
            '<p>This is a chunked response after 2 seconds. ' +
            'Should be displayed before 5-second chunk arrives.</p>\n';
        response.write(html);
    }, 2000);

}).listen(1337, null);
