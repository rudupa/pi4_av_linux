################################################################################
#
# av_services
#
################################################################################

AV_SERVICES_VERSION = local
AV_SERVICES_SITE = $(BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH)/../external/av_services
AV_SERVICES_SITE_METHOD = local
AV_SERVICES_LICENSE = Apache-2.0
AV_SERVICES_LICENSE_FILES = LICENSE
AV_SERVICES_DEPENDENCIES = libcurl
AV_SERVICES_PKGDIR = $(BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH)/package/av_services
PI4_RUNTIME_DIR = $(BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH)/../pi4

define AV_SERVICES_INSTALL_RUNTIME_FILES
	$(INSTALL) -d $(TARGET_DIR)/etc/av-core
	$(INSTALL) -d $(TARGET_DIR)/etc/pi4
	$(INSTALL) -d $(TARGET_DIR)/opt/av/pi4
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/gateway.conf $(TARGET_DIR)/etc/av-core/gateway.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/health.conf $(TARGET_DIR)/etc/av-core/health.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/logger.conf $(TARGET_DIR)/etc/av-core/logger.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/ota.conf $(TARGET_DIR)/etc/av-core/ota.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/orchestrator.conf $(TARGET_DIR)/etc/av-core/orchestrator.conf
	$(INSTALL) -m 0644 $(PI4_RUNTIME_DIR)/config/runtime.yaml $(TARGET_DIR)/etc/pi4/runtime.yaml
	cp -a $(PI4_RUNTIME_DIR)/src $(TARGET_DIR)/opt/av/pi4/
	cp -a $(PI4_RUNTIME_DIR)/config $(TARGET_DIR)/opt/av/pi4/
	cp -a $(PI4_RUNTIME_DIR)/scripts $(TARGET_DIR)/opt/av/pi4/
	$(INSTALL) -d $(TARGET_DIR)/var/lib/av-core/ota
	$(INSTALL) -d $(TARGET_DIR)/var/log/av-core
endef

AV_SERVICES_POST_INSTALL_TARGET_HOOKS += AV_SERVICES_INSTALL_RUNTIME_FILES

define AV_SERVICES_INSTALL_INIT_SYSV
	$(INSTALL) -D -m 0755 $(AV_SERVICES_PKGDIR)/S99avcore $(TARGET_DIR)/etc/init.d/S99avcore
endef

define AV_SERVICES_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 0644 $(AV_SERVICES_PKGDIR)/av-core-orchestrator.service \
		$(TARGET_DIR)/usr/lib/systemd/system/av-core-orchestrator.service
	$(INSTALL) -D -m 0644 $(AV_SERVICES_PKGDIR)/av-core-gateway.service \
		$(TARGET_DIR)/usr/lib/systemd/system/av-core-gateway.service
	$(INSTALL) -D -m 0644 $(AV_SERVICES_PKGDIR)/av-core-health.service \
		$(TARGET_DIR)/usr/lib/systemd/system/av-core-health.service
	$(INSTALL) -D -m 0644 $(AV_SERVICES_PKGDIR)/av-core-logger.service \
		$(TARGET_DIR)/usr/lib/systemd/system/av-core-logger.service
	$(INSTALL) -D -m 0644 $(AV_SERVICES_PKGDIR)/av-core-ota.service \
		$(TARGET_DIR)/usr/lib/systemd/system/av-core-ota.service
	$(INSTALL) -D -m 0644 $(AV_SERVICES_PKGDIR)/av-core-pi4-runtime.service \
		$(TARGET_DIR)/usr/lib/systemd/system/av-core-pi4-runtime.service
	$(INSTALL) -d $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -sf /usr/lib/systemd/system/av-core-orchestrator.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/av-core-orchestrator.service
	ln -sf /usr/lib/systemd/system/av-core-gateway.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/av-core-gateway.service
	ln -sf /usr/lib/systemd/system/av-core-health.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/av-core-health.service
	ln -sf /usr/lib/systemd/system/av-core-logger.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/av-core-logger.service
	ln -sf /usr/lib/systemd/system/av-core-ota.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/av-core-ota.service
	ln -sf /usr/lib/systemd/system/av-core-pi4-runtime.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/av-core-pi4-runtime.service
endef

$(eval $(cmake-package))
