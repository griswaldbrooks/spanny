# spanny
Robot arm project for lightning talk on mdspan.
Presented as a ligthening talk at CppCon 2023 and ROSCon 2023.

# CppCon 2023
[![CppCon 2023 Video](https://img.youtube.com/vi/FZZ3CDnBEx4/maxresdefault.jpg)](https://youtu.be/FZZ3CDnBEx4)

# ROSCon 2023
[![ROSCon 2023](/presentation/images/roscon2023spanny.png)](https://vimeo.com/879001243?share=copy#t=1172.026)

# YouTube
[![Youtube Video](https://img.youtube.com/vi/DFnZIpwfZoc/maxresdefault.jpg)](https://youtu.be/DFnZIpwfZoc)

# Development Container
Build a new development image
```shell
mkdir -p ~/.spanny/ccache
export UID=$(id -u) export GID=$(id -g); docker compose -f compose.dev.yml build
```
Start an interactive development container
```shell
docker compose -f compose.dev.yml run development
```
Build the repository in the container
```shell
username@spanny-dev:~/ws$ cmake -S src/spanny/ -B build
username@spanny-dev:~/ws$ cmake --build build
```

# Run
```shell
username@spanny-dev:~/ws$ ./build/spanny
```
