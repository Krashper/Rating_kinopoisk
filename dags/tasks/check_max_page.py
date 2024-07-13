from airflow.models import Variable
import logging


def check_max_page() -> bool:
    try:
        page = int(Variable.get("cur_page"))
        max_page = int(Variable.get("max_page"))

        if page > max_page:
            return False
        
        else:
            return True
    
    except Exception as e:
        logging.error("Error during checking max_page: ", e)