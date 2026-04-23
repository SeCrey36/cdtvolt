from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from courses.models import Enrollment


def _split_fio(full_name: str) -> tuple[str, str, str]:
    parts = (full_name or "").split()
    if len(parts) >= 3:
        return parts[0], parts[1], " ".join(parts[2:])
    if len(parts) == 2:
        return parts[0], parts[1], ""
    if len(parts) == 1:
        return parts[0], "", ""
    return "", "", ""


def _get_template_path() -> Path:
    configured = getattr(settings, "CONTRACT_TEMPLATE_PATH", "")
    if configured:
        return Path(configured)
    return Path(settings.BASE_DIR) / "templates" / "contract.docx"


def generate_contract_for_enrollment(enrollment: Enrollment, overwrite: bool = True) -> str:
    """Generate a contract DOCX from template and save it into Enrollment.contract_file.

    Returns relative file path in media storage.
    Raises ValidationError if required data/template are missing.
    """
    template_path = _get_template_path()
    if not template_path.exists():
        raise ValidationError(f"Шаблон договора не найден: {template_path}")

    try:
        from docxtpl import DocxTemplate
    except ImportError as exc:
        raise ValidationError("Пакет docxtpl не установлен. Установите: pip install docxtpl") from exc

    course = enrollment.course
    if not course:
        raise ValidationError("Нельзя сформировать договор: у записи нет выбранного курса")

    instructor = course.instructors.first()
    if not instructor:
        raise ValidationError("Нельзя сформировать договор: у курса не назначен преподаватель")

    psur, pn, potch = (
        enrollment.student_surname,
        enrollment.student_first_name,
        enrollment.student_patronymic,
    )
    if not psur and not pn:
        psur, pn, potch = _split_fio(enrollment.student_name)

    tsur = instructor.last_name or _split_fio(instructor.name)[0]
    tn = instructor.first_name or _split_fio(instructor.name)[1]
    totch = instructor.patronymic or _split_fio(instructor.name)[2]

    context = {
        "tsur": tsur,
        "tn": tn,
        "totch": totch,
        "tser": instructor.passport_series,
        "tnum": instructor.passport_number,
        "tvid": instructor.passport_issued_by,
        "telephone": instructor.contract_phone,
        "psur": psur,
        "pn": pn,
        "potch": potch,
        "pser": enrollment.student_passport_series,
        "pnum": enrollment.student_passport_number,
        "pvid": enrollment.student_passport_issued_by,
    }

    doc = DocxTemplate(str(template_path))
    doc.render(context)

    filename = f"contract_enrollment_{enrollment.pk}.docx"
    tmp_path = Path(settings.MEDIA_ROOT) / "contracts" / filename
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(tmp_path))

    # Save through storage so admin can download via FileField.
    with tmp_path.open("rb") as fh:
        content = ContentFile(fh.read())
        save_name = f"contracts/{filename}"
        if overwrite and enrollment.contract_file:
            enrollment.contract_file.delete(save=False)
        enrollment.contract_file.save(save_name, content, save=False)

    enrollment.save(update_fields=["contract_file"])
    return enrollment.contract_file.name
