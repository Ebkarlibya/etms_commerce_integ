
newPassword = document.querySelector("#new_password");
repeatNewPassword = document.querySelector("#repeat_new_password");

passwordLengthAlert = document.querySelector("#password_length_alert");
resetSuccessAlert = document.querySelector("#reset_success_alert");
passwordMismatchAlert = document.querySelector("#password_mismatch_alert");
passwordResetFaildAlert = document.querySelector("#password_reset_faild_alert");
passwordWeakAlert = document.querySelector("#password_weak_alert");



submitBtn = document.querySelector("#submitBtn");

submitBtn.addEventListener("click", function() {

    if(newPassword.value !== repeatNewPassword.value) {
        passwordMismatchAlert.hidden = false;
        setTimeout(function() {
            passwordMismatchAlert.hidden = true;
        }, 3000);
        return;
    }
    if(newPassword.value.length < 6) {
        passwordLengthAlert.hidden = false;
        setTimeout(function() {
            passwordLengthAlert.hidden = true;
        }, 3000);
        return
    }
    submitBtn.disabled = true;

    frappe.call({
        type: "POST",
        method: "etms_commerce_integ.auth.handle_password_reset",
        args: {
            resetKey: document.location.search.split("=")[1],
            newPassword: newPassword.value
        },
        callback: function(r) {
            
            if(r.message.message == "password_reset_accepted") {
                resetSuccessAlert.hidden = false;
                newPassword.disabled = true;
                repeatNewPassword.disabled = true;
                submitBtn.disabled = true;
            }

            if(r.message.message == "password_reset_rejected") {
                passwordResetFaildAlert.hidden = false;
                setTimeout(function() {
                    passwordResetFaildAlert.hidden = true;
                    submitBtn.disabled = false;
                }, 3000);
            }

            if(r.message.message == "password_weak") {
                passwordWeakAlert.hidden = false;
                setTimeout(function() {
                    passwordWeakAlert.hidden = true;
                    submitBtn.disabled = false;
                }, 5000);
            }

 

        }
    })

});



function testPassword(pwString) {
    var strength = 0;

    strength += /[A-Z]+/.test(pwString) ? 1 : 0;
    strength += /[a-z]+/.test(pwString) ? 1 : 0;
    strength += /[0-9]+/.test(pwString) ? 1 : 0;
    strength += /[\W]+/.test(pwString) ? 1 : 0;

    switch(strength) {
        case 3:
            return false;
        case 4:
            return true
        default:
            
            return false;
    }
}