#!/bin/bash
rsync -az frontend/dist/client/ pradu.us:~/git/study/frontend/dist/client/
rsync -az frontend/public/vendor/ pradu.us:~/git/study/frontend/public/vendor
