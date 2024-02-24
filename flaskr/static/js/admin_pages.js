$(document).ready(function () {

    const lessonTypeSelect = document.getElementById('lesson_type');
    const additionalField1Container = document.getElementById('div_lesson_capacity');
    const additionalField2Container = document.getElementById('div_additional_instructors');

    lessonTypeSelect.addEventListener('change', function () {
        if (this.value === 'ind') {
            additionalField1Container.style.display = 'none';
            additionalField2Container.style.display = 'none';
        } else if (this.value === 'group') {
            additionalField1Container.style.display = '';
            additionalField2Container.style.display = '';
        }
    });
});