jQuery.aaFooterAds = function(source) {
  var self = this;
  self.init = function() {
    jQuery(source).each(function(i, item) {
      adLink = jQuery('#' + item.id + ' a');
      if (item.isFlash) {
        if (!jQuery.flash.available) {
          adLink.append(
              '<img src="' + item.imgSrc + '" alt="' + item.altText + '" />');
        } else {
          jQuery(adLink).flash({
            swf: item.flashSrc,
            height: item.height,
            width: item.width,
            expressInstall: true
          });
        }
      }
      adLink.attr('title', item.altText);
      if (item.target.indexOf('http') != -1) {
        temp = function() {
          captureExtClickThru(
              item.target, item.anchorLocation, item.altText,
              item.repositoryName, item.repositoryId, item.locale,
              item.isFlash);
        };
        item.isFlash ? adLink.mouseup(temp) : adLink.click(temp);
      }
      if (item.openInNewWin == 'Y') {
        temp = function() {
          window.open(
              this.href, '',
              'scrollbars=yes,toolbar=yes,resizable=yes,status=yes,location=no,menubar=no,width=700,height=480,top=1,left=385');
          return false;
        };
        item.isFlash ? adLink.mouseup(temp) : adLink.click(temp);
      } else {
        if (item.isFlash) {
          adLink.mouseup(function() {
            location.href = this.href;
          });
        }
      }
    });
  };
  self.init();
};