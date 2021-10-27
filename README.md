# PIG
PayInJustice, just for a homonymic, I call it PIG instead PIJ
preparing: Truffle, Ganache, Django, MySQL
It's easy to run it but there is something you should pay attention. First, you must guarantee port in truffle's config-file and ganache are the same one. Then, run `truffle migrate --reset` instead `truffle migrate` if you have migrated it before. And finally, tricky~, there is no final one now.
At the beginning, you should deploy the etherum by using command `truffle compile` and `truffle migrate (--reset)` in folder of contract ('Contact/' Folder in my pro, I have a spelling error but it doesn't matter). Then, boot the Ganache AppImage and choose (or initialize) a virtual etherum. Last step, command `python manage.py runserver 127.0.0.1:8000`. You can use other sockets and I like using the localhost:8000 for test.
And at the end, hope you all like it. Thanks.
