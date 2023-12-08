from celery import shared_task
from sqlalchemy import func
import flask_excel as excel
from model import db, Product, Order
from mail import send_message


@shared_task(ignore_result=False)
def download_csv():
    result = (
        db.session.query(
            Order.order_id,
            Order.product_name,
            func.ifnull(func.sum(Order.quantity), 0).label('total_sold'),
            func.ifnull(func.sum(Order.quantity * Order.product_price), 0).label('total_expenditure'),
        )
        .group_by(Order.product_name)
        .all()
    )
    if len(result) == 0:
        return None
    output = excel.make_response_from_query_sets(result,
                                                 column_names=['order_id', 'product_name',
                                                               'total_sold', 'total_expenditure'],
                                                 file_type="csv")
    file_name = "summary.csv"
    with open(file_name, "wb") as f:
        f.write(output.data)

    return file_name


@shared_task(ignore_result=False)
def download_csv2():
    result = db.session.query(
        Product.product_id,
        Product.product_name,
        Product.product_quantity,
        Product.product_price,
    ).all()

    output = excel.make_response_from_query_sets(result,
                                                 column_names=['product_id', 'product_name',
                                                               'product_quantity', 'product_price'],
                                                 file_type="csv")
    file_name = "stock.csv"
    with open(file_name, "wb") as f:
        f.write(output.data)
    return file_name


@shared_task(ignore_result=True)
def monthly_report(to, msg, body):
    send_message(to, msg, body)
    return "OK"


@shared_task(ignore_result=True)
def daily_reminder(to, msg, body):
    send_message(to, msg, body)
    return "OK"


@shared_task(ignore_result=True)
def manager_account_status(to, msg, body):
    send_message(to, msg, body)
    return "OK"
