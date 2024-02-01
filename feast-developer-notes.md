Documenting the resources I have followed while trying to understand the feast codebase.

1) Have basic idea of protobuf and the syntax to create the proto object. Personally i have been through this
   (tutorial)[https://protobuf.dev/getting-started/pythontutorial/].
2) Having a good understanding of the GRPC protocol will help. Personally I have ended up watching (this video)[https://www.youtube.com/watch?v=psYAhc9JUyo] of implementing simple server client communication using GRPC protocol and proto.
3) Read the Development guide and all the contribute.md and readme.md files. \
   https://docs.feast.dev/project/development-guide#feast-data-storage-format \
   https://github.com/feast-dev/feast/tree/master/docs/getting-started \
   https://github.com/feast-dev/feast/blob/master/java/CONTRIBUTING.md \
   https://github.com/feast-dev/feast/blob/master/java/README.md
5) This is the path all the shared proto definitions are located - https://github.com/feast-dev/feast/tree/master/protos
6) This the path having the code related to feast UI. Feast UI is a React based application.
7) python click package will facilitate out of the box options to create the CLI applications. Feast is using this library. for more info refer (website)[https://click.palletsprojects.com/en/8.1.x/].