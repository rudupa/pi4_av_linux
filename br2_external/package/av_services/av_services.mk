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

# Install the submodule source tree into the target image for on-target build/deploy.
define AV_SERVICES_INSTALL_TARGET_CMDS
	$(INSTALL) -d $(TARGET_DIR)/opt/av_services
	cp -a $(@D)/* $(TARGET_DIR)/opt/av_services/
	rm -rf $(TARGET_DIR)/opt/av_services/.git
endef

$(eval $(generic-package))
