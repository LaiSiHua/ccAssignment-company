// delete button - pop up window 
const btnDelete= document.querySelectorAll('.btn-delete');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('Are you sure you want to delete it?')){
        e.preventDefault();
      }
    });
  })
}

// reject button - pop up window 
const btnReject= document.querySelectorAll('.btn-reject');
if(btnReject) {
  const btnArray = Array.from(btnReject);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('Are you sure you want to reject it?')){
        e.preventDefault();
      }
    });
  })
}

// approve button - pop up window 
const btnApprove= document.querySelectorAll('.btn-approve');
if(btnApprove) {
  const btnArray = Array.from(btnApprove);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('Are you sure you want to approve it?')){
        e.preventDefault();
      }
    });
  })
}

// close flash message 
function delete_flash(flash){
  $(flash).parent().remove()
}