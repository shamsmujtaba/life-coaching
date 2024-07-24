
// ---------------------------Our news section popup-------------------

document.addEventListener('DOMContentLoaded', () => {
    const seeMoreButtons = document.querySelectorAll('.see-more-button');
    const popup = document.getElementById('popup');
    const timePickerModal = document.getElementById('timePickerModal');
    const popupImage = document.getElementById('popupImage');
    const popupTitle = document.getElementById('popupTitle');
    const popupDescription = document.getElementById('popupDescription');
    const closePopup = document.getElementById('closePopup');
    
    seeMoreButtons.forEach(button => {
        button.addEventListener('click', () => {
            const image = button.getAttribute('data-image');
            const title = button.getAttribute('data-title');
            const description = button.getAttribute('data-description');
            popupImage.src = baseUrl +image;
            popupTitle.textContent = title;
            popupDescription.textContent = description;
            
            popup.style.display = 'block';
        });
    });
    
    closePopup.addEventListener('click', () => {
        popup.style.display = 'none';
    });
    
    window.addEventListener('click', (event) => {
        if (event.target === popup) {
            popup.style.display = 'none';
        }
    });
});



const header = document.querySelector(".page-header");
let toggleClass = "is-sticky";
let inactive = "inactive";
let dNone = "d-none";

window.addEventListener("scroll", () => {
  const currentScroll = window.scrollY;
  if (currentScroll > 200) {
      header.classList.add(toggleClass);
      header.classList.remove(inactive);
      header.classList.remove(dNone);
  } else if(currentScroll > 100 && currentScroll < 199 ){
    header.classList.add(inactive);
    header.classList.remove(toggleClass);
    header.classList.remove(dNone);
  } else if(currentScroll<99 ) {
      header.classList.remove(inactive);
      header.classList.remove(toggleClass);
    //   header.classList.add(dNone);
    //   header.classList.add(dNone);
  } 
  animation('.slide-wraper-right')
  animation('.slide-wraper-left')
  animation('.wraper-animated')
});

function animation(claslist) {
    let slideWrappers = document.querySelectorAll(claslist);
    let threshold = 500; // Adjust this threshold as needed
    slideWrappers.forEach(slideWrapper => {
        let triggerPosition = slideWrapper.getBoundingClientRect().top;
        if (triggerPosition < threshold) {
            slideWrapper.classList.add('active');
        } else {
            // slideWrapper.classList.remove('active');
        }
    });
  }


//   ------------Time Selection---------------------
$('.time-block').on('click', function(){
    let timePickerModal = document.getElementById('timePickerModal');
    if ($(this).hasClass('enabled')) {
        var hiddenInput = $(this).find('input[type="hidden"]');
        var time = hiddenInput.val();
        // $(this).addClass('active');
        alert(time);
        $('#select_time').val(time)
        console.log($('#select_time').val())
        timePickerModal.style.display = 'none';
        removeActiveSlot()
    }
})
function setActiveSlot() {
    let timeBlocks=document.querySelectorAll('.time-block');
    let iniTime=$('#select_time').val()
    timeBlocks.forEach(timeBlock => { 
        var hiddenInput = timeBlock.querySelector('input[type="hidden"]');
        if(iniTime == hiddenInput.value) {
             timeBlock.classList.add('active');
        }
    })
}
function removeActiveSlot() {
    let timeBlocks=document.querySelectorAll('.time-block');
    timeBlocks.forEach(timeBlock => { 
        
        timeBlock.classList.remove('active');
        
    })
}