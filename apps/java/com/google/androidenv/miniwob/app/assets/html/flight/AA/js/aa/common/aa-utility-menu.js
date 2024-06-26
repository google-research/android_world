var delete_VPNR;
jQuery(document).ready(function() {
  try {
    if (typeof aa_Utilities === 'undefined') {
      jQuery('head').append(
          '<script type=\'text/javascript\' src=\'/apps/common/js/jquery/aacom/utilities/aaUtilities.js\'><\/script>');
    }
  } catch (err) {
  }
  delete_VPNR = createVPNR();
  delete_VPNR.initDeleteVPNRModal();
});
createVPNR = function() {
  var delete_VPNR = {
    aaUtil_delete_VPNR: new aa_Utilities(),
    btns: [
      {
        name: vpnr_okMessage,
        callback: function forwardLogin() {
          deleteVirtualPNR();
          var url = jQuery('#loginURL').val();
          window.location = url;
        },
        cssClass: 'btn',
        closeDialog: true
      },
      {
        name: vpnr_cancelMessage,
        cssClass: 'btn btn-secondary',
        closeDialog: true
      }
    ],
    deleteVPNRModal: function() {
      var VPNR = jQuery('#virtualPNR').val(), status = jQuery('#status').val();
      if (VPNR == 'true' && status != 'Purchased') {
        this.aaUtil_delete_VPNR.aaDialog('#modal_deleteVPNRModal')
            .openDialog(jQuery('#loginLogoutLink'));
        jQuery(window).scrollTop(0);
      } else {
        var url = jQuery('#loginURL').val();
        window.location = url;
      }
    },
    initDeleteVPNRModal: function() {
      this.aaUtil_delete_VPNR.aaDialog(
          '#modal_deleteVPNRModal',
          {width: 'small', buttons: this.btns, toggleScroll: true});
    }
  };
  return delete_VPNR;
};
function deleteVPNRModal() {
  delete_VPNR.deleteVPNRModal();
}