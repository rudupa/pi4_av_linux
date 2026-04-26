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

define AV_SERVICES_INSTALL_RUNTIME_FILES
	$(INSTALL) -d $(TARGET_DIR)/etc/av-core
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/gateway.conf $(TARGET_DIR)/etc/av-core/gateway.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/health.conf $(TARGET_DIR)/etc/av-core/health.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/logger.conf $(TARGET_DIR)/etc/av-core/logger.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/ota.conf $(TARGET_DIR)/etc/av-core/ota.conf
	$(INSTALL) -m 0644 $(AV_SERVICES_PKGDIR)/orchestrator.conf $(TARGET_DIR)/etc/av-core/orchestrator.conf
	$(INSTALL) -d $(TARGET_DIR)/var/lib/av-core/ota
	$(INSTALL) -d $(TARGET_DIR)/var/log/av-core
endef

AV_SERVICES_POST_INSTALL_TARGET_HOOKS += AV_SERVICES_INSTALL_RUNTIME_FILES

define AV_SERVICES_INSTALL_INIT_SYSV
	$(INSTALL) -D -m 0755 $(AV_SERVICES_PKGDIR)/S99avcore $(TARGET_DIR)/etc/init.d/S99avcore
endef

$(eval $(cmake-package))
