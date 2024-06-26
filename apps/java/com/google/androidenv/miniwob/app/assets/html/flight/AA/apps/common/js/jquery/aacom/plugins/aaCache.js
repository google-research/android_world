var aaCache = (function($j) {
  var cache = {};
  function _get(key) {
    if (!cache[key]) {
      cache[key] = $j(key);
    }
    return cache[key];
  }
  function _remove(key) {
    if (cache.hasOwnProperty(key)) {
      return (delete cache[key]);
    }
    return true;
  }
  return {get: _get, remove: _remove};
}(jQuery));