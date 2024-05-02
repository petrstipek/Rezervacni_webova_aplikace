/**
 * FileName: flash.js
 * Description: Flash script for handling flash messages, Mainly its hiding behaviour.
 * Author: Petr Štípek
 * Date Created: 2024
 */

$(document).ready(function () {
    setTimeout(function () {
        $(".alert").not('.persistent').slideUp(500, function () {
            $(this).remove();
        });
    }, 5000);

});