# Machine Census drift report

Generated 2026-08-17 23:52 AST on vicar-mainframe.


| Item | dl | vicar-mainframe |
|---|---|---|
| os | Ubuntu 24.04.4 LTS | Ubuntu 24.04.3 LTS |  <-- DIFFERS
| kernel | 6.8.0-107-generic | 6.8.0-55-generic |  <-- DIFFERS
| gpu | NVIDIA GeForce RTX 5090, 595.58.03, 32607 MiB | NVIDIA GeForce RTX 5090, 580.65.06, 32607 MiB; NVIDIA GeForce RTX 5090, 580.65.06, 32607 M |
| ram | 125Gi | 251Gi |
| apt package count | 3477 | 3341 |  <-- DIFFERS
| snap count | 34 | 38 |  <-- DIFFERS
| R | 4.6.1 | 4.6.1 |
| system python3 | 3.12.3 | 3.12.3 |
| conda envs (named) | OK_CV, sam3reef, tf-gpu-env, vicarius-tagfab, vicarius-taglab | OK_CV, sam3reef, tf-gpu-env, vicarius-tagfab, vicarius-taglab |
| ollama models | none | qwen3-coder:30b 18 GB; qwen3.5:122b 81 GB; gpt-oss:120b 65 GB; qwen3.6:27b 17 GB; qwen3-em |  <-- DIFFERS

## Major applications

| App | dl | vicar-mainframe |
|---|---|---|
| claude_code | absent @ absent | 2.1.195 @ /home/bizon/.npm-global/bin/claude |  <-- DIFFERS
| docker | 28.0.1 @ /usr/bin/docker | 28.0.1 @ /usr/bin/docker |
| ffmpeg | 6.1.1-3ubuntu5 @ /usr/bin/ffmpeg | 6.1.1-3ubuntu5 @ /usr/bin/ffmpeg |
| gh | 2.45.0 @ /usr/bin/gh | 2.74.0-19-gea8fc856e @ /snap/bin/gh |  <-- DIFFERS
| metashape | 2.3.1 @ /opt/metashape-pro | 2.2.2 @ /opt/metashape-pro |  <-- DIFFERS
| node | 18.19.1 @ /usr/bin/node | 18.19.1 @ /usr/bin/node |
| ollama | 0.20.2 @ /usr/local/bin/ollama | 0.32.0 @ /usr/local/bin/ollama |  <-- DIFFERS
| splashtop | 3.8.2.0-1 @ dpkg | 3.8.2.0-1 @ dpkg |
| synology_drive | 8.0.3-17892 @ /opt/Synology/SynologyDrive | 8.0.1-17885 @ /opt/Synology/SynologyDrive |  <-- DIFFERS

## Apt set differences

Only on dl (200): anydesk, bzip2-doc, cccl-13-3, cmatrix, cuda-cccl-13-2, cuda-command-line-tools-13-2, cuda-command-line-tools-13-3, cuda-compiler-13-2, cuda-compiler-13-3, cuda-crt-13-2, cuda-crt-13-3, cuda-ctadvisor-13-3, cuda-cudart-13-2, cuda-cudart-13-3, cuda-cudart-dev-13-2, cuda-cudart-dev-13-3, cuda-culibos-dev-13-2, cuda-culibos-dev-13-3, cuda-cuobjdump-13-2, cuda-cuobjdump-13-3, cuda-cupti-13-2, cuda-cupti-13-3, cuda-cupti-dev-13-2, cuda-cupti-dev-13-3, cuda-cuxxfilt-13-2, cuda-cuxxfilt-13-3, cuda-documentation-13-2, cuda-documentation-13-3, cuda-driver-dev-13-2, cuda-driver-dev-13-3, cuda-gdb-13-2, cuda-gdb-13-3, cuda-libraries-13-2, cuda-libraries-13-3, cuda-libraries-dev-13-2, cuda-libraries-dev-13-3, cuda-nsight-13-2, cuda-nsight-compute-13-2, cuda-nsight-compute-13-3, cuda-nsight-systems-13-2 ...

Only on vicar-mainframe (24): gitkraken, libgdk-pixbuf-xlib-2.0-0, libgdk-pixbuf2.0-0, libllvm19, libnvidia-cfg1-580, libnvidia-common-580, libnvidia-compute-580, libnvidia-decode-580, libnvidia-egl-wayland1, libnvidia-encode-580, libnvidia-extra-580, libnvidia-fbc1-580, libnvidia-gl-580, libnvidia-gpucomp-580, nvidia-compute-utils-580, nvidia-dkms-580-open, nvidia-driver-580-open, nvidia-firmware-580, nvidia-kernel-common-580, nvidia-kernel-source-580-open, nvidia-utils-580, socat, synology-assistant, xserver-xorg-video-nvidia-580

## VICARIUS desktop integration

| Check | dl | vicar-mainframe |
|---|---|---|
| vicarius pinned | True | True |
| screensaver pinned | True | True |
| aspect-toggle pinned | True | True |
| launcher files | True | True |
| gnome extension | True | True |

Total flagged differences: 10
