# -*- coding: utf-8 -*-
from django.db import models
import datetime

from PIL import Image
from StringIO import StringIO
from markdown2 import Markdown

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.defaultfilters import slugify

from tickets.func import rand_16

import configuration.customise

from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(
        max_length=50,
        help_text='Shows up on pages.'
        )
    slug = models.SlugField(
        help_text='Will be used in class names, so you can style categories differently.'
        )
    sort = models.IntegerField(
        help_text='Low to high, sorts the sidebar.'
        )

    def __str__(self): return self.name


@python_2_unicode_compatible
class Show(models.Model):
    class Meta:
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'

    name = models.CharField(max_length=64)

    slug = models.SlugField(
                    blank=True,
                    help_text='Used in the URL of the detail page, leave blank to auto-generate.'
                    )

    location = models.CharField(
                    max_length=30,
                    default=configuration.customise.DEFAULT_LOCATION,
                    help_text='Will show up alongside show, you can hide this with CSS if needed.'
                    )

    description = models.TextField(
                    help_text='A short description, one paragraph only.'
                    )

    long_description = models.TextField(
                    blank=True,
                    help_text='Shows up on the detail page, this field is written in Markdown. ' +
                    '(See <a href="http://www.darkcoding.net/software/markdown-quick-reference/">Markdown reference</a> for reference.'
                    )

    poster = models.ImageField(
                    upload_to='posters',
                    blank=True, null=True,
                    help_text='Upload a large image, we will automatically create smaller versions to use.'
                    )

    poster_wall = models.ImageField(upload_to='posters', blank=True, null=True)
    poster_page = models.ImageField(upload_to='posters', blank=True, null=True)
    poster_tiny = models.ImageField(upload_to='posters', blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    category = models.ForeignKey('Category')

    IMAGE_SIZES = {'poster_wall': (126, 178),
                   'poster_page': (256, 362),
                   'poster_tiny': (50, 71)}

    def is_current(self):
        today = datetime.date.today()
        if today > self.end_date:
            return False
        else:
            return True

    def show_sold_out(self):
        if self.occurrence_set.count() > 0:
            for occ in self.occurrence_set.all():
                if occ.sold_out() is False:
                    return False
            return True
        else:
            return False

    def has_occurrences(self):
        occs = Occurrence.objects.filter(show=self)
        if len(occs) > 0:
            return True
        else:
            return False

    def gen_thumbs(self):
        img = Image.open(self.poster.path)
        if img.mode not in ('L', 'RGB'):    # Convert to RGB
            img = img.convert('RGB')
        for field_name, size in self.IMAGE_SIZES.iteritems():
            field = getattr(self, field_name)
            working = img.copy()
            working.thumbnail(size, Image.ANTIALIAS)
            fp = StringIO()
            working.save(fp, "JPEG", quality=95)
            cf = InMemoryUploadedFile(
                fp, 
                None, 
                self.poster.name, 
                'image/jpeg',
                fp.len, 
                None
                )
            field.save(name=field_name+"_"+self.poster.name, content=cf, save=True)

    def long_markdown(self):
        md = Markdown()
        return md.convert(self.long_description)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        have_orig = False
        if self.pk:
            orig = Show.objects.get(pk=self.pk)
            have_orig = True
        super(Show, self).save(*args, **kwargs)
        if not self.poster_wall and not self.poster_page \
        and not self.poster_tiny and self.poster:
            self.gen_thumbs()
        elif have_orig and self.poster != orig.poster:
            self.gen_thumbs()

    def __str__(self):
        return self.name


class OccurrenceManager(models.Manager):

    def get_available(self, show):
        today = datetime.date.today()
        time = datetime.datetime.now()
        occs = Occurrence.objects.filter(show=show).filter(date__gte=today).order_by('date', 'time')
        ret = []
        for oc in occs:
            hour = oc.time.hour
            close_time = hour - oc.hours_til_close
            if oc.sold_out():
                pass
                break
            if oc.date == today and time.hour >= close_time:
                pass
                break
            else:
                ret.append((oc.id, oc.datetime_formatted()))
        return ret


@python_2_unicode_compatible
class Occurrence(models.Model):

    class Meta:
        verbose_name = 'Occurrence'
        verbose_name_plural = 'Occurrences'

    show = models.ForeignKey(Show)
    date = models.DateField()
    time = models.TimeField(default=configuration.customise.DEFAULT_TIME)
    maximum_sell = models.PositiveIntegerField(
                default=configuration.customise.DEFAULT_MAX_SELL,
                help_text='The maximum number of tickets we will allow to be reserved.'
                )

    hours_til_close = models.IntegerField(
                default=configuration.customise.DEFAULT_HOURS_TIL_CLOSE,
                help_text='Hours before \'time\' that we will stop reservations being made.'
                )
    unique_code = models.CharField(max_length=16)

    objects = OccurrenceManager()

    def day_formatted(self):
        return self.date.strftime('%A')

    def time_formatted(self):
        return self.time.strftime('%-I%p').lower()

    def datetime_formatted(self):
        return self.date.strftime('%A %d %B ') + \
            self.time.strftime('%-I%p').lower()

    def tickets_sold(self):
        tickets = Ticket.objects.filter(occurrence=self).filter(cancelled=False)
        sold = 0
        for ticket in tickets:
            sold += ticket.quantity
        return sold

    def sold_out(self):
        if self.tickets_sold() >= self.maximum_sell:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = rand_16()
        super(Occurrence, self).save(*args, **kwargs)
        self.show.save()

    def __str__(self):
        return self.show.name + " on " + str(self.date) + " at " + str(self.time)


@python_2_unicode_compatible
class Ticket(models.Model):

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    occurrence = models.ForeignKey(Occurrence)
    stamp = models.DateTimeField(auto_now=True)
    person_name = models.CharField(max_length=80)
    email_address = models.EmailField(max_length=80)
    quantity = models.IntegerField(default=1)
    cancelled = models.BooleanField(default=False)
    unique_code = models.CharField(max_length=16)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = rand_16()
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return self.occurrence.show.name + \
            " on " + str(self.occurrence.date) + \
            " at " + str(self.occurrence.time) + \
            " for " + self.person_name
