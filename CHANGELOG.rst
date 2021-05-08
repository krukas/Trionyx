[3.0.0] - 08-05-2021
--------------------

**Compatibility breaking changes: Upgrade to Django 3.2 and reset DB migrations for JSONField**

Added
~~~~~
- Add option to make model view/add/change/delete admin only
- Make CELERY_BROKER_URL set by env
- Add vuex.js
- Add option to hide footer
- Add settings to always filter list queryset

Changed
~~~~~~~
- Panel component title attribute now accepts component
- Add helper functions to get/set local data
- Add helper function get_current_user and make get_current_user available in tasks if a user started the task
- Celery hooks are auto loaded from settings
- Remove /media/ from xsendfile
- Search by field label name
- Inline show non field errors
- Allow model_url to have an empty viewname

Fixed
~~~~~
- AppSettings crashes on migrate because variable table does not yet exists
- Fix ProgrammingError: relation "django_cache" does not exist
- Fix verbose name not saved
- Graph widget only first 30 records instead of lasts 30 records
- Button dialog custom url error

[2.2.0] - 03-09-2020
--------------------

**Compatibility breaking changes: Remove -custom for code url path**

Added
~~~~~
- Allow apps to add global css/js files
- Add Field component
- Add option to hide table header
- Add options to disable auditlog
- App settings can be overridden with system variables
- Add config to disable viewing of model
- Add option should_render to components
- New projects will print emails to console in development
- Add options to set custom create/edit permission on form
- Add permission to dashboard widgets and widget data
- Add celery command for development with auto reload on file change
- Add ImageField renderer
- Add foreign field renderer that renders object with `a` tag
- Add Json field renderer
- Add action column to list view with actions view,edit and delete (remove row click)
- Add graph dashboard widget + improve widget options

Changed
~~~~~~~
- Make raised Exceptions more explicit
- Update models to use settings.AUTH_USER_MODEL and in code to get_user_model()
- Remove -custom for code url path
- Allow for muliple dialog reload options
- Change select_related to prefetch_related to prevent join errors on not null fields
- Do model clean on objects for MassUpdate
- Several small Improvement
- Add no_link options to renderers with an `a` tag, for list view its won't render value in `a` tag
- Close list fields popover on outside click
- Change many to many field renderer to use `a` tags

Fixed
~~~~~~~
- Form Datetimepicker format is not set in __init__
- Summernote popovers remain on page if dialog was closed


[2.1.3] - 08-04-2020
--------------------
Added
~~~~~
- Add support for __format__ for LazyFieldRenderer (used by model verbose_name)
- Add support for CTRL+Click and scroll wheel click on list view item to open new tab

Changed
~~~~~~~
- Remove Google fonts

Fixed
~~~~~
- #51 Filters datepicker won't work if previous selected field was a select
- Mass update crashes on collecting fields from forms when custom __init__ is used


[2.1.2] - 04-04-2020
--------------------
Fixed
~~~~~
- Greater then filter not working


[2.1.1] - 02-04-2020
--------------------
Added
~~~~~
- Add login redirect to previous visited page

Fixed
~~~~~
- Fix multiple enumerations are added to list view on slow load
- Fix drag column order on list view out order after drag event
- get_current_request not working in streaming response


[2.1.0] - 12-02-2020
--------------------
Added
~~~~~
- Add create_reusable_app command
- Add ProgressBar component
- Add Unordered and Ordered list components
- Add LineChart, BarChart, PieChart and DoughnutChart component
- Add options to register data function for a widget
- Add support for file upload in dialog
- Add full/extra-large size options to dialog
- Add link target option to header buttons
- Add Date value renderer
- Add current url to dialog object
- Add Link component
- Add component option to lock object
- Add footer with Trionyx and app version
- Add changelog dialog with auto show on version change
- Add command to generate favicon
- Add Ansible upgrade playbook for quickstart
- Add user API token reset link
- Add JS helper runOnReady function
- Add basic-auth authentication view
- Add ajax form choices and multiple choices field

Changed
~~~~~~~
- Update translations
- Add traceback stack to DB logs with no Exception
- Set max_page of 1000 for API and default page size to 25
- Moved depend JS to static files
- Change logging to file rotation for quickstart project
- Improve Table component styling options

Fixed
~~~~~
- Widget config popup is blank
- Fix form layout Depend not working on create/update view
- Fix widget config_form_class is not set
- Fix list_value_renderer crashes on non string list items
- Fix list load loop on fast reloads (eq spam next button)
- Fix Makefile translate commands
- Fix CreateDialog permission check wasn't working
- Fix model alias tabs not working
- Fix Quickstart reusable app
- Fix log messages is not formatted in db logger
- Fix BaseTask can be executed to fast
- Fix prevent large header titles pushing buttons and content away


[2.0.2] - 24-12-2019
--------------------
Fixed
~~~~~
- Fix inlineforms not working in popup
- Widget config dialog wasn't shown


[2.0.1] - 19-12-2019
--------------------
Added
~~~~~
- Add helper function for setting the Watson search language

Changed
~~~~~~~
- Small improvements to prevent double SQL calls
- #39 Make python version configurable for Makefile

Fixed
~~~~~
- Ansible role name is not found
- JsonField does not work in combination with jsonfield module


[2.0.0] - 11-12-2019
--------------------

**Compatibility breaking changes: drop support for python 3.5**

Added
~~~~~
- Add generic model sidebar
- Add Summernote wysiwyg editor
- Add more tests and MyPy
- Add getting started guide to docs and improve README
- Add more bootstrap components
- Add frontend layout update function
- Add system variables
- Add helper class for app settings
- Add support for inline forms queryset
- Add company information to settings
- Add price template filter
- Add ability for forms to set page title and submit label
- Add options to display create/change/delete buttons
- Add signals for permissions

Changed
~~~~~~~
- Drop support for python 3.5
- Improve api serializer registration
- Improve list view column sizes
- Move from vitualenv to venv
- Make inline formset dynamic
- Make delete button available on edit page
- Make header buttons generic and show them on list and edit page
- Header buttons can be shown based on tab view 

Fixed
~~~~~
- Cant go to tab if code is same as code in jstree
- Several small fixes and changes


[1.0.5] - 31-10-2019
--------------------
Fixed
~~~~~
- Fixed model overwrite configs/forms/menu


[1.0.4] - 31-10-2019
--------------------

Changed
~~~~~~~
- Improved new project creation

Fixed
~~~~~
- Filter related choices are not shown


[1.0.3] - 30-10-2019
--------------------
Fixed
~~~~~
- Fixed to early reverse lookup
- Fixed not all quickstart files where included


[1.0.2] - 30-10-2019
--------------------
Changed
~~~~~~~
- Dialog form initial also uses GET params
- model_url accept GET params as dict
- Improve Button component
- ComponentFieldsMixin fields can now render a Component
- Add option to Component to force update object
- Base Component can be used as an holder for Components to be rendered
- Add debug comments to Component output

Fixed
~~~~~
- Delete dialog does not return `success` boolean
- Fixed html component not rendering html and tag not closed


[1.0.1] - 29-10-2019
--------------------
Fixed
~~~~~
- Fixed verbose name has HTML


[1.0.0] - 29-10-2019
--------------------

**Compatibility breaking changes: Migrations are cleared**

Added
~~~~~
- Add get_current_request to utils
- Add DB logger
- Add options to disable create/update/delete for model
- Add debug logging for form errors
- Add audit log for models
- Add user last_online field
- Add support for inline formsets
- Add rest API support
- Add option to add extra buttons to header
- Add search to list fields select popover
- Add Dashboard
- Add Audtilog dashboard widget
- Add model field summary widget
- Add auto import Trionyx apps with pip entries
- Add data choices lists for countries/currencies/timezones
- Add language support + add Dutch translations
- Add user timezone support
- Add CacheLock contectmanager
- Add locale_overide and send_email to user
- Add mass select selector to list view
- Add mass delete action
- Add Load js/css from forms and components
- Add view and edit permissions with jstree
- Add mass update action
- Add BaseTask for tracking background task progress
- Add support for related fields in list and auto add related to queryset
- Add layout component find/add/delete
- Add model overwrites support that are set with settings
- Add renderers for email/url/bool/list

Changed
~~~~~~~
- Set fallback for user profile name and avatar
- Improve header visibility
- Make filters separate vuejs component + function to filter queryset
- Improve theme colors and make theme square
- Update AdminLTE+plugins and Vue.js and in DEBUG use development vuejs
- Refactor inline forms + support single inline form
- Auditlog values are rendered with renderer
- Changed pagination UX
- Show filter label instead of field name

Fixed
~~~~~
- Project create settings BASE_DIR was incorrect
- Menu item with empty filtered childs is shown
- Make verbose_name field not required
- Global search is activated on CTRL commands
- Auditlog delete record has no name
- Created by was not set
- Auditlog gives false positives for Decimal fields
- Render date: localtime() cannot be applied to a naive datetime
- Fix model list dragging + fix drag and sort align
- Fixed None value is rendered as the string None

[0.2.0] - 04-06-2019
--------------------

**Compatibility breaking changes**

Added
~~~~~
- Form register and refactor default forms to use this
- Add custom form urls + shortcut model_url function
- Add layout register + layout views
- Add model verbose_name field + change choices to use verbose_name query
- Add permission checks and hide menu/buttons with no permission

Changed
~~~~~~~
- Render fields for verbose_name and search title/description
- Move all dependencies handling to setup.py
- Upgrade to Django 2.2 and update other dependencies
- refactor views/core from Django app to Trionyx package
- Rename navigation to menu
- Move navigtaion.tabs to views.tabs
- Quickstart project settings layout + add environment.json

Fixed
~~~~~
- Cant search in fitler select field
- Datetimepicker not working for time
- Travis build error
- Button component


[0.1.1] - 30-05-2019
--------------------
Fixed
~~~~~
- Search for not indexed models
- Lint errors


[0.1.0] - 30-05-2019
--------------------
Added
~~~~~
- Global search
- Add filters to model list page
- Set default form layouts for fields

Changed
~~~~~~~
- Search for not indexed models

Fixed
~~~~~
- Make datepicker work with locale input format
- On menu hover resize header 
- Keep menu state after page refresh
- Search for not indexed models