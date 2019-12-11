from django.test import TestCase
from trionyx import layout as l  # noqa E741

from trionyx.trionyx.models import User


class ModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="info@trionyx.com")
        self.layout = l.Layout(
            l.Row(
                l.Column6(
                    l.Panel(
                        'Left panel',
                        id='left-panel'
                    )
                ),
                l.Column6(
                    l.Panel(
                        'Right panel',
                        id='right-panel'
                    )
                )
            )
        )

    def test_layout_path(self):
        panel, parent = self.layout.find_component_by_path('row.column6[1].panel')
        self.assertEqual(panel.title, 'Right panel')

    def test_layout_id(self):
        panel, parent = self.layout.find_component_by_id('right-panel')
        self.assertEqual(panel.title, 'Right panel')

    def test_remove_component(self):
        self.layout.delete_component(path='row.column6.panel')
        self.layout.delete_component(id='right-panel')
        self.assertInHTML("""
        <div class="row">
            <div class="col-md-6"></div>
            <div class="col-md-6"></div>
        </div>
        """, self.layout.render())

    def test_remove_top_component(self):
        self.layout.delete_component(path='row')
        self.assertInHTML("""<div id="{}"></div>""".format(self.layout.id), self.layout.render())

    def test_remove_invalid_component(self):
        with self.assertRaises(Exception):
            self.layout.delete_component(path='some random path')

    def test_remove_no_params_component(self):
        with self.assertRaises(Exception):
            self.layout.delete_component()

    def test_add_component(self):
        self.layout.add_component(l.Img(), path='row.column6[1].panel', append=True)
        self.layout.add_component(l.Img(), id='left-panel', append=True)

        self.assertInHTML("""
        <div class="row">
            <div class="col-md-6">
                <div id="component-left-panel">
                    <div class="panel panel-default">
                        <div class="panel-heading">Left panel</div>
                        <div class="panel-collapse">
                            <img width="100%" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div id="component-right-panel">
                    <div class="panel panel-default">
                        <div class="panel-heading">Right panel</div>
                        <div class="panel-collapse">
                            <img width="100%" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, self.layout.render())

    def test_input(self):
        self.assertHTMLEqual(l.Input(name='test').render({}), """
        <div class="form-group no-margin ">
            <input type="text" class="form-control" name="test" />
        </div>
        """)

    def test_button(self):
        button = l.Button('Trionyx')
        button.set_object(self.user)
        self.assertHTMLEqual(button.render({}), """
        <button class="btn btn-flat bg-theme" onclick="window.location.href='/model/trionyx/user/{id}/'; return false;">
            Trionyx
        </button>
        """.format(id=self.user.id))

    def test_button_dialog(self):
        button = l.Button('Trionyx', dialog=True, dialog_reload_tab='general')
        button.set_object(self.user)
        self.assertHTMLEqual(button.render({}), """
        <button class="btn btn-flat bg-theme" onClick="openDialog('/model/trionyx/user/{id}/', {{ callback:function(data, dialog){{
                if (data.success) {{
                    dialog.close();
                    trionyx_reload_tab('general');
                }}
            }} }}); return false;">
            Trionyx
        </button>
        """.format(id=self.user.id))

    def test_table(self):
        html = l.Table(
            [['column1', 'column2', 'column3']],
            {
                'label': 'Column 1',
            },
            {
                'label': 'Column 2',
            },
            {
                'label': 'Column 3',
            },
            footer=[
                [
                    ['Footer', '123'],
                ],
                {
                    'colspan': 2,
                },
                {
                    'class': 'text-right',
                }
            ]
        ).render({})
        self.assertHTMLEqual(html, """
        <table class="table table-condensed">
            <thead>
                <tr>
                    <th>Column 1</th>
                    <th>Column 2</th>
                    <th>Column 3</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>column1</td>
                    <td>column2</td>
                    <td>column3</td>
                </tr>
            </tbody>
            <tfooter class="">
                <tr>
                    <td colspan="2">Footer</td>
                    <td class="text-right">123</td>
                </tr>
            </tfooter>
        </table>
        """)
