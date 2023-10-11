from sqlalchemy import select, delete, desc
from sqlalchemy.sql.functions import random, count, max
from sqlalchemy.exc import IntegrityError
from Db import Session
from helpers import generate_random_number, NEXT_RANGE, MAX_RANGE
from models import AvailableKeys, BookedKeys


def book_available_keys(number_of_elem):
    retry = 5
    great_flag = False
    # session context manager take care of automatic closing of session and
    # begin method will open a transaction which will do commit and rollback automatically, once session context is end.
    while retry:
        try:
            with Session.begin() as sess:


                # fetching from table
                # with_for_update will hold row level locks till commit this current transaction,
                # it will put other update, delete and select with with_for_update on hold. but normal select without
                # with_for_update will work and give old data.

                # statement = select(AvailableKeys).order_by(random()).limit(number_of_elem).with_for_update()
                # order by Random is slow as it creates new column at runtime and fill it with random values using
                # random function  of sql. then it will do sorting on the basis of that new column.

                # so instead we are already storing random values in Db in new column, to save time on this
                # calculation step

                statement = select(AvailableKeys).order_by(desc(AvailableKeys.order_key)).limit(number_of_elem).with_for_update()
                user_obj = sess.scalars(statement).all()
                keys_list = [i.seq for i in user_obj]

                if len(keys_list) < number_of_elem:
                    bulk_add_available_key(sess)
                    retry -= 1
                    great_flag = True
                    continue

                great_flag = False
                # deleting form table

                statement = delete(AvailableKeys).where(AvailableKeys.seq.in_(keys_list))
                sess.execute(statement)

                # adding into booked table
                booked_keys = [BookedKeys(seq=key.seq, order_key=key.order_key) for key in user_obj]
                sess.bulk_save_objects(booked_keys)
            break
        except IntegrityError as e:
            # if we get integrity error that means the key we are trying to book is already booked
            # so, we will try again
            # but with current setup it is not possible, as we are already adding lock for booking keys
            # so only one user acn book keys at a time and only after deleting keys we are doing booking.
            # So race condition will not occur
            retry -= 1
    else:
        keys_list = 'unable to generate keys'
        if great_flag:
            keys_list += '; try with lesser range'

    return keys_list


def free_booked_key(key):

    try:
        with Session.begin() as sess:

            statement = delete(BookedKeys).where(BookedKeys.seq == key)
            sess.execute(statement)
            sess.add(AvailableKeys(seq=key, order_key=generate_random_number(key)))

    except IntegrityError as e:
        print('key already exists in Available table')

    with Session.begin() as sess:
        res = sess.scalar(select(AvailableKeys).where(AvailableKeys.seq == key))
        res = res.seq
    return res


def bulk_add_available_key(session):
    start_range = get_max_range_in_db(session) + 1
    if start_range > MAX_RANGE:
        raise Exception('reach to keys limit')
    end_range = start_range + NEXT_RANGE
    if end_range > MAX_RANGE:
        end_range = MAX_RANGE

    objects = [
        AvailableKeys(seq=key, order_key=generate_random_number(key)) for key in range(start_range, end_range)
    ]

    session.bulk_save_objects(objects)
    return objects


def get_max_range_in_db(session):

    statement1 = select(max(AvailableKeys.seq))
    res1 = session.scalars(statement1).first()
    statement2 = select(max(BookedKeys.seq))
    res2 = session.scalars(statement2).first()
    if res2 is None:
        res2 = 0
    if res1 is None:
        res1 = 0
    return res1 if res1 > res2 else res2

