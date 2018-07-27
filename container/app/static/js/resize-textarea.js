$( document ).ready(function() {
  function expandTextarea(id) {
    max_height = 800;
      document.getElementById(id).addEventListener('keyup', function() {
        var height = this.scrollHeight;
        if (height > max_height) {
          height = max_height;
          this.style.overflow = 'auto';
        } else {
          this.style.overflow = 'hidden';
        }

        this.style.height = height + 'px';

      }, false);
  }

  expandTextarea('json-textarea');
});
