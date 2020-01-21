# MARS 2019

Codebase for the MARS club @ UVA

## Setup Manual Control

Launch the server script on Jetson nano

```bash
python -m mars_2019.jetson.server
```

Then launch the gamepad state interpreter

```bash
python -m mars_2019.laptop.gamepad_encoder
```

## Compile jetson-inference on host

1. Install CUDA-10.0/10.1, https://www.tensorflow.org/install/gpu#ubuntu_1804_cuda_101

2. Make sure it is in your path, see

https://docs.nvidia.com/cuda/archive/10.1/cuda-installation-guide-linux/index.html#post-installation-actions

3. Download TensorRT 6.0.1 (tar ball), and copy headers and shared libraries to system include path

```bash
cd TensorRT-6.x.x.x
sudo cp -r include/* /usr/include/x86_64-linux-gnu/
sudo cp -r lib/* /usr/lib/x86_64-linux-gnu/
```

4. Clone the repository

```bash
git clone --recursive https://github.com/hanzhi713/jetson-inference
```

Open CMakeLists.txt and replace `aarch64-linux-gnu` with `x86_64-linux-gnu`.

5. Build and install

```bash
cd jetson-inference
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
```