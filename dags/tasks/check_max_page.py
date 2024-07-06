from airflow.models import Variable


def check_max_page() -> bool:
    page = int(Variable.get("cur_page"))
    max_page = int(Variable.get("max_page"))

    if page > max_page:
        return False
    
    else:
        return True