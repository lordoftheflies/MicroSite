from django.test import TestCase
from django.test import Client
from pages.forms import PageForm, MenuForm
from micro_admin.models import User
from pages.models import Page, Contact, Menu
from micro_blog.models import Country
from django.core.urlresolvers import reverse


class pages_forms_test(TestCase):

    def test_pageforms(self):
        self.client = Client()
        form = PageForm(
            data={
                'title': 'Page',
                'content': 'page_content',
                'slug' : 'slug',
                'meta_data' : 'meta_title',
            })
        self.assertTrue(form.is_valid())

    def test_Menuform(self):
        self.client = Client()
        form = MenuForm(
            data={'title': 'main', 'status': 'on'})
        self.assertTrue(form.is_valid())


# models test
class pages_models_test(TestCase):

    def create_page(
            self,
            title="simple page",
            content="simple page content",
            slug="page",
            meta_data="meta_title",
            ):
        return Page.objects.create(title=title, content=content, slug=slug, meta_data=meta_data)

    def test_whatever_creation(self):
        w = self.create_page()
        self.assertTrue(isinstance(w, Page))
        self.assertEqual(w.__unicode__(), w.title)


class contact_models_test(TestCase):

    def create_contact(
            self, domain="simple page",
            domain_url="simple page content",
            country="",
            enquery_type="feedback",
            full_name="simple page",
            message="simple page content",
            email='contact@mp.com'):
        return Contact.objects.create(
            domain="https://micropyramid.com",
            domain_url="https://micropyramid.com",
            country="india",
            enquery_type="feedback")

    def test_whatever_creation(self):
        w = self.create_contact()
        self.assertTrue(isinstance(w, Contact))


class pages_views_test_with_employee(TestCase):

    def setUp(self):
        self.client = Client()
        self.employee = User.objects.create_user(
            'testemployee', "testemployee@micropyramid.com", 'pwd')

    def test_views_with_employee_login(self):
        user_login = self.client.login(
            username='testemployee@micropyramid.com', password='pwd')
        self.assertTrue(user_login)

        response = self.client.get('/portal/content/page/new/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/portal/content/page/edit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/portal/content/page/delete/1/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = self.client.get('/portal/content/menu/new/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/portal/content/menu/edit/3/')
        self.assertTrue(response.status_code, 404)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/portal/content/menu/delete_menu/1/')
        self.assertTrue(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = self.client.get('/page-test/')
        self.assertTrue(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')


class pages_views_test(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            'pyramid@mp.com', 'microtest', 'mp')
        self.country = Country.objects.create(name='US', code='us', slug='us')
        self.page = Page.objects.create(title='Page', content='page_content', slug='page', country=self.country, is_active=True, is_default=True)
        self.menu = Menu.objects.create(title='django', url='micro.in', status='on', lvl=1, country=self.country)

    def test_views(self):
        user_login = self.client.login(username='microtest', password='mp')
        self.assertTrue(user_login)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/portal/content/page/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/portal/content/page/new/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/portal/content/page/new/',
            {
                'title': 'Page2',
                'content': 'page_content',
                'slug': 'slug',
                'meta_data': 'meta_title',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str('Page created successfully') in response.content.decode('utf8'))

        response = self.client.post(
            '/portal/content/page/new/',
            {
                'content': 'page_content',
                'meta_data': 'meta_description',
            })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(str('Page created successfully') in response.content.decode('utf8'))

        response = self.client.get('/portal/content/menu')
        self.assertEqual(response.status_code, 301)

        response = self.client.get('/portal/content/menu/new/')
        self.assertEqual(response.status_code, 200)

        # With right input
        response = self.client.post(
            '/portal/content/menu/new/', {'title': 'main', 'url': 'micro.in/m', 'status': 'on', 'parent': self.menu.id, 'country': self.country.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str('Menu created successfully') in response.content.decode('utf8'))

        # Test cases for changing menu order
        response = self.client.post(
            '/portal/content/menu/1/order/', {'mode': 'down'})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(str('Menu order updated successfully') in response.content.decode('utf8'))

        response = self.client.post(
            '/portal/content/menu/1/order/', {'mode': 'up'})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(str('You cant move up.') in response.content.decode('utf8'))

        # with wrong input
        response = self.client.post(
            '/portal/content/menu/new/', {'url': 'micro.in/m', 'status': 'on', 'parent': Menu.objects.all().last().id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(str('successfully') in response.content.decode('utf8'))

        response = self.client.get(
            '/portal/content/page/edit/'+str(self.page.id)+'/')
        self.assertEqual(response.status_code, 200)

        # chnage menu status to off
        response = self.client.get('/portal/content/page/status/'+str(self.page.id)+'/')
        self.assertEqual(response.status_code, 302)

        # change menu status to on
        response = self.client.get('/portal/content/page/status/'+str(self.page.id)+'/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/portal/content/menu/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/portal/content/page/edit/'+str(self.page.id)+'/',
            {
                'title': 'Page',
                'content': 'page_content',
                'slug' : 'page',
                'meta_data' : 'meta_title',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str('successfully') in response.content.decode('utf8'))

        response = self.client.post(
            '/portal/content/page/edit/'+str(self.page.id)+'/',
            {
                'content': 'page_content',
                'meta_data': 'meta_description',
            })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(str('successfully') in response.content.decode('utf8'))

        # chnage menu status to off
        response = self.client.get('/portal/content/menu/status/1/')
        self.assertEqual(response.status_code, 302)

        # change menu status to on
        response = self.client.get('/portal/content/menu/status/1/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/portal/content/menu/edit/3/')
        self.assertTrue(response.status_code, 200)

        response = self.client.post(
            '/portal/content/menu/new/', {'title': 'main menu', 'url': 'micro.in/m', 'status': 'on', 'parent': Menu.objects.all().last().id, 'country': self.country.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str('Menu created successfully') in response.content.decode('utf8'))

        response = self.client.post(
            '/portal/content/menu/edit/3/', {'title': 'main2', 'status': 'on', 'country_id': self.country.slug})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(str('updated successfully') in response.content.decode('utf8'))

        url = reverse('pages:edit_menu', kwargs={'pk': '3'})
        response = self.client.post(url, {'id': '3', 'title': 'main2', 'url': 'micro.in/menu', 'status': 'on', 'parent': 1, 'country_id': self.country.slug})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            str('updated successfully') in response.content.decode('utf8'))

        response = self.client.post(url, {'title': 'main2', 'url': 'micro.in/menu', 'status': 'on', 'parent': 2, 'country_id': self.country.slug})
        self.assertTrue(response.status_code, 200)
        # self.assertTrue('can not choose the same as parent' in response.content)

        response = self.client.post(url, {'url': 'micro.in', 'status': 'on', 'country_id': self.country.slug, 'parent': Menu.objects.all().last().id})
        self.assertTrue(response.status_code, 200)
        self.assertFalse(str('successfully') in response.content.decode('utf8'))

        response = self.client.post(
            '/portal/content/menu/new/', {'title': 'menu2', 'url': 'http://micro.com/menu2', 'status': 'on', 'country_id': self.country.id, 'parent': Menu.objects.all().last().id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str('Menu created successfully') in response.content.decode('utf8'))

        # Test cases for changing menu order
        response = self.client.post(
            '/portal/content/menu/1/order/', {'mode': 'down'})
        self.assertTrue(response.status_code, 200)

        response = self.client.post(
            '/portal/content/menu/1/order/', {'mode': 'up'})
        self.assertTrue(response.status_code, 200)

        response = self.client.post(url, {'title': 'main2', 'status': 'on', 'parent': 2, 'country_id': self.country.slug, 'parent': Menu.objects.all().last().id})
        self.assertTrue(response.status_code, 200)
        self.assertTrue(str('updated successfully') in response.content.decode('utf8'))

        response = self.client.get('/portal/content/menu/delete_menu/1/')
        self.assertTrue(response.status_code, 200)

        response = self.client.get('/'+str(self.page.slug)+'/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/portal/content/page/delete/'+str(self.page.id)+'/')
        self.assertEqual(response.status_code, 302)
