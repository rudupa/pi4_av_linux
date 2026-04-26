################################################################################
#
# pi4_feature_check
#
################################################################################

PI4_FEATURE_CHECK_VERSION = local
PI4_FEATURE_CHECK_SITE = $(BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH)/package/pi4_feature_check
PI4_FEATURE_CHECK_SITE_METHOD = local
PI4_FEATURE_CHECK_LICENSE = MIT
PI4_FEATURE_CHECK_LICENSE_FILES =
PI4_FEATURE_CHECK_PKGDIR = $(BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH)/package/pi4_feature_check

define PI4_FEATURE_CHECK_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(PI4_FEATURE_CHECK_PKGDIR)/pi4_feature_check.sh \
		$(TARGET_DIR)/usr/local/sbin/pi4_feature_check.sh
endef

define PI4_FEATURE_CHECK_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 0644 $(PI4_FEATURE_CHECK_PKGDIR)/pi4-feature-check.service \
		$(TARGET_DIR)/usr/lib/systemd/system/pi4-feature-check.service
	$(INSTALL) -d $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -sf /usr/lib/systemd/system/pi4-feature-check.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/pi4-feature-check.service
endef

$(eval $(generic-package))
