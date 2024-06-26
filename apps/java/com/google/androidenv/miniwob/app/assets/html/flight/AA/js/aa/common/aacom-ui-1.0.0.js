function AAcom() {
  var args = Array.prototype.slice.call(arguments), callback = args.pop(),
      modules = (args[0] && typeof args[0] === 'string') ? args : args[0], i;
  if (!(this instanceof AAcom)) {
    return new AAcom(modules, callback);
  }
  if (!modules || modules == '*') {
    modules = [];
    for (i in AAcom.modules) {
      if (AAcom.modules.hasOwnProperty(i)) {
        modules.push(i);
      }
    }
  }
  for (i = 0; i < modules.length; i += 1) {
    AAcom.modules[modules[i]](this);
  }
  callback(this);
}
AAcom.prototype = {
  _name: 'AACom Sandbox',
  _version: '1.0.0',
  _vars: {},
  getName: function() {
    return this._name;
  },
  getVersion: function() {
    return this._version;
  },
  getProperty: function(key) {
    return this._vars[key];
  },
  setProperty: function(obj) {
    for (var key in obj) {
      if (!(key in this._vars)) {
        this._vars[key] = obj[key];
      }
    }
  }
};
AAcom.modules = {};