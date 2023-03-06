let settingsElement = document.querySelector('.settings');
let closeElement = document.querySelector('.close-settings');
let blur = document.querySelector('.blur');
let successfullyElement = document.querySelector('.successfully');
let unsuccessfullyElement = document.querySelector('.unsuccessfully');

settingsElement.onclick = closeElement.onclick = blur.onclick = toggleSettingsVisibility

// Включение, выключение настроек
function toggleSettingsVisibility() {
    document.querySelector('.settings-menu').classList.toggle('hidden')
    document.querySelector('.blur').classList.toggle('hidden')
};


// Включение и выключение какого-либо html элемента
function appearanceEffect(element) {
    element.classList.toggle('hidden')
    setTimeout(() => {element.classList.toggle('hidden')}, 2000) 
};


// AJAX для обновления аватара пользователя
let avatarImage = document.getElementById('avatar-image');
let avatarForm = document.getElementById('avatar-form');
let avatarInput = document.getElementById('avatar-input');

avatarImage.onclick = function() {avatarInput.click();};

avatarInput.onchange = function() {
    let formData = new FormData(avatarForm);
    $.ajax({
        url: avatarForm.action,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            avatarImage.src = data.url;
            console.log(data)
            appearanceEffect(successfullyElement)
        },
        error: function(data) {
            console.log('Error:', data);
            appearanceEffect(unsuccessfullyElement)
        }
    });
};


// AJAX для обновления статуса пользователя
let statusForm = document.getElementById('status-form')
let statusInput = document.getElementById('status-value')
let statusConfirm = document.querySelector('.confirm-status')

statusConfirm.onclick = function() {
    let data = new FormData(statusForm);
    $.ajax({
        url: statusForm.action,
        type: 'POST',
        data: data,
        processData: false,
        contentType: false,
        success: function(data) {
            console.log(data)
            appearanceEffect(successfullyElement)
        },
        error: function(data) {
            console.log('Error:', data);
            appearanceEffect(unsuccessfullyElement)
        }
    });
}

