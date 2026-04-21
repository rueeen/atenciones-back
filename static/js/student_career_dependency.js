(function () {
  if (window.__studentCareerDependencyInitialized) {
    return;
  }
  window.__studentCareerDependencyInitialized = true;

  const EMPTY_OPTION = '<option value="">Seleccione una carrera</option>';

  const findStudentForm = (element) => element?.closest('form[data-student-form="true"]');

  const setCareerOptions = (careerSelect, careers, selectedCareerId = null) => {
    careerSelect.innerHTML = EMPTY_OPTION;

    careers.forEach((career) => {
      const option = document.createElement('option');
      option.value = String(career.id);
      option.textContent = career.name;
      if (selectedCareerId && String(career.id) === String(selectedCareerId)) {
        option.selected = true;
      }
      careerSelect.appendChild(option);
    });
  };

  const loadCareers = async ({ form, academicAreaId, selectedCareerId = null }) => {
    const careerSelect = form.querySelector('#id_career');
    const careersUrl = form.dataset.careersUrl;

    if (!careerSelect || !careersUrl) {
      return;
    }

    if (!academicAreaId) {
      setCareerOptions(careerSelect, []);
      return;
    }

    careerSelect.disabled = true;
    setCareerOptions(careerSelect, []);

    try {
      const response = await fetch(`${careersUrl}?academic_area_id=${encodeURIComponent(academicAreaId)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });

      if (!response.ok) {
        throw new Error('No se pudieron cargar las carreras.');
      }

      const data = await response.json();
      const careers = Array.isArray(data.careers) ? data.careers : [];
      setCareerOptions(careerSelect, careers, selectedCareerId);
    } catch (error) {
      setCareerOptions(careerSelect, []);
    } finally {
      careerSelect.disabled = false;
    }
  };

  document.addEventListener('change', (event) => {
    if (event.target.id !== 'id_academic_area') {
      return;
    }

    const form = findStudentForm(event.target);
    if (!form) {
      return;
    }

    loadCareers({ form, academicAreaId: event.target.value });
  });
})();
