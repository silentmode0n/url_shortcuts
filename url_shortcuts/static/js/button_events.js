function handleCopyToClipboard(text) {
  const cb = navigator.clipboard;
  cb.writeText(text).then(() => alert('Ссылка скопирована.'));
  }

function handleConfirmTransition(link, message, target) {
  if (confirm(message)) {

    handleTransition(link, target)

  }
}

function handleTransition(link, target) {
  let a= document.createElement('a');
  if (target != null) {
    a.target= target;
  }
  a.href= link;
  a.click();
}