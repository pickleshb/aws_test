from django.test import TestCase
from django.core.files import File
from models import *
from markdown2 import Markdown

import datetime


class StaticPageTest(TestCase):

    def test_list_view(self):
        response = self.client.get('/list/')
        self.assertEqual(response.status_code, 200)

    def test_sidebar_view(self):
        response = self.client.get('/sidebar/')
        self.assertEqual(response.status_code, 200)


class BookTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category',slug='test',sort=1)
        start_date = datetime.date.today()+datetime.timedelta(days=2)
        end_date = datetime.date.today()+datetime.timedelta(days=5)
        Show.objects.create(
            name='Test Show', 
            location='Somewhere', 
            description='Some Info',
            long_description='Some more info', 
            poster=File(open('test/test_poster.jpg')),
            start_date=start_date, 
            end_date=end_date, 
            category=cat
            )

    def test_show_exists(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.name, 'Test Show')

    def test_book_form(self):
        response = self.client.get('/book/1/')
        self.assertEqual(response.status_code, 200)

    def test_sold_out_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.sold_out(), False)

    def test_has_occurrences_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.has_occurrences(), False)


class ShowTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category',slug='test',sort=1)
        start_date = datetime.date.today()+datetime.timedelta(days=2)
        end_date = datetime.date.today()+datetime.timedelta(days=5)
        Show.objects.create(
            name='Test Show', 
            location='Somewhere', 
            description='Some Info',
            long_description='Some more info', 
            poster=File(open('test/test_poster.jpg')),
            start_date=start_date, 
            end_date=end_date, 
            category=cat
            )

        Occurrence.objects.create(
            show=Show.objects.get(pk=1),
            date=datetime.date.today(),
            time=datetime.datetime.now(),
            maximum_sell=2,
            hours_til_close=2,
            unique_code=rand_16(),
            )

        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )

    def test_is_current_false(self):
        show = Show.objects.get(pk=1)
        show.end_date = datetime.date.today() + datetime.timedelta(days=-5)
        self.assertEqual(show.is_current(), False)


    def test_sold_out_true(self):
        show = Show.objects.get(pk=1)
        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )
        self.assertEqual(show.sold_out(), True)

    def test_has_occurrences_true(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.is_current(), True)

    def test_show_name(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.__str__(), show.name)

    def test_occurrence_sold_out_false(self):
        occ = Occurrence.objects.get(pk=1)
        self.assertEqual(occ.sold_out(), False)

    def test_markdown(self):
        show = Show.objects.get(pk=1)
        md = Markdown()
        ld_md = md.convert(show.long_description)
        self.assertEqual(show.long_markdown(), ld_md)

    def test_datetime_formatted(self):
        occ = Occurrence.objects.get(pk=1)
        day_format = occ.date.strftime('%A')
        time_format = occ.time.strftime('%-I%p').lower()
        datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I%p').lower()

        self.assertEqual(occ.day_formatted(), day_format)
        self.assertEqual(occ.time_formatted(), time_format)
        self.assertEqual(occ.datetime_formatted(), datetime_format)

    def test_occurrence_str(self):
        occ = Occurrence.objects.get(pk=1)
        occ_str = occ.show.name + " on " + str(occ.date) + " at " + str(occ.time)
        self.assertEqual(occ.__str__(), occ_str)

    def test_ticket_str(self):
        tick = Ticket.objects.get(pk=1)
        tick_str = tick.occurrence.show.name + \
            "on" + str(tick.occurrence.date) + \
            "at" + str(tick.occurrence.time) + \
            "for" + tick.person_name

        self.assertEqual(tick.__str__(), tick_str)