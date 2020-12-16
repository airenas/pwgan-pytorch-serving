-include Makefile.options
MODEL_PATH?=./model
cuda?=0
torch?=1.7.0
#####################################################################################
service=airenas/pwgan-pytorch-serving
version=0.2
version-gpu=0.3
commit_count=$(shell git rev-list --count HEAD)
#####################################################################################
test:
	pytest
#####################################################################################
prepare-env:
	conda create -y -n pwgan-$(DEVICE) python=3.8.5
drop-env:
	conda remove --name pwgan-$(DEVICE) --all
install-req:
ifeq ($(DEVICE),cpu)
	pip install torch==$(torch)+cpu -f https://download.pytorch.org/whl/torch_stable.html
	pip install -r requirements.txt
else
	pip install -r requirements.txt
	pip install -r requirements_gpu.txt
endif

run:
	CUDA_VISIBLE_DEVICES=$(cuda) MODEL_PATH=$(MODEL_PATH) MODEL_NAME=$(MODEL_NAME) \
		DEVICE=$(DEVICE) PORT=$(PORT) python run.py
########### SERVICE ################################################################
logs:
	mkdir -p $@
install-service: deploy/service/pwgan.service | logs
	cp deploy/service/pwgan.service /etc/systemd/system/
	systemctl enable pwgan.service
uninstall-service:
	systemctl disable pwgan.service
	rm -f /etc/systemd/system/pwgan.service
deploy/service/pwgan.service: deploy/service/pwgan.service.in
	cat $< | envsubst > $@
run-service:
	. ~/miniconda3/etc/profile.d/conda.sh; conda activate pwgan-$(DEVICE); \
		CUDA_VISIBLE_DEVICES=$(cuda) MODEL_PATH=$(MODEL_PATH) MODEL_NAME=$(MODEL_NAME) \
		DEVICE=$(DEVICE) PORT=$(PORT) python run.py
########### DOCKER ##################################################################
########### DOCKER ##################################################################
tag=$(service):$(version).$(commit_count)
dbuild: $(dist_dir)/$(executable_name)
	docker build -t $(tag) ./

dpush: dbuild
	docker push $(tag)
########### DOCKER GPU ##############################################################
tag-gpu=$(service)-gpu:$(version-gpu).$(commit_count)
dbuild-gpu: $(dist_dir)/$(executable_name)
	docker build -f Dockerfile_gpu -t $(tag-gpu) ./

dpush-gpu: dbuild-gpu
	docker push $(tag-gpu)
#####################################################################################
.PHONY:
	 dbuild dpush
