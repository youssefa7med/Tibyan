@echo off
pushd "%cd%"
echo Running PyTorch CUDA installation script...
venv\Scripts\python install_pytorch_cuda.py
popd
