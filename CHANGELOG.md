### [develop]

**Compatibility breaking changes: drop support for python 3.5**

#### Added
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

#### Changed
- Drop support for python 3.5
- Improve api serializer registration
- Improve list view column sizes
- Move from vitualenv to venv
- Make inline formset dynamic
- Make delete button available on edit page
- Make header buttons generic and show them on list and edit page
- Header buttons can be shown based on tab view 

#### Fixed
- Cant go to tab if code is same as code in jstree
- Several small fixes and changes


### [1.0.5] - 31-10-2019
#### Fixed
- Fixed model overwrite configs/forms/menu


### [1.0.4] - 31-10-2019
#### Changed
- Improved new project creation

#### Fixed
- Filter related choices are not shown


### [1.0.3] - 30-10-2019
#### Fixed
- Fixed to early reverse lookup
- Fixed not all quickstart files where included


### [1.0.2] - 30-10-2019
#### Changed
- Dialog form initial also uses GET params
- model_url accept GET params as dict
- Improve Button component
- ComponentFieldsMixin fields can now render a Component
- Add option to Component to force update object
- Base Component can be used as an holder for Components to be rendered
- Add debug comments to Component output

#### Fixed
- Delete dialog does not return `success` boolean
- Fixed html component not rendering html and tag not closed


### [1.0.1] - 29-10-2019
#### Fixed
- Fixed verbose name has HTML


### [1.0.0] - 29-10-2019

**Compatibility breaking changes: Migrations are cleared**

#### Added
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

#### Changed
- Set fallback for user profile name and avatar
- Improve header visibility
- Make filters separate vuejs component + function to filter queryset
- Improve theme colors and make theme square
- Update AdminLTE+plugins and Vue.js and in DEBUG use development vuejs
- Refactor inline forms + support single inline form
- Auditlog values are rendered with renderer
- Changed pagination UX
- Show filter label instead of field name

#### Fixed
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

### [0.2.0] - 04-06-2019 

**Compatibility breaking changes**

#### Added
- Form register and refactor default forms to use this
- Add custom form urls + shortcut model_url function
- Add layout register + layout views
- Add model verbose_name field + change choices to use verbose_name query
- Add permission checks and hide menu/buttons with no permission

#### Changed
- Render fields for verbose_name and search title/description
- Move all dependencies handling to setup.py
- Upgrade to Django 2.2 and update other dependencies
- refactor views/core from Django app to Trionyx package
- Rename navigation to menu
- Move navigtaion.tabs to views.tabs
- Quickstart project settings layout + add environment.json

#### Fixed
- Cant search in fitler select field
- Datetimepicker not working for time
- Travis build error
- Button component


### [0.1.1] - 30-05-2019
#### Fixed
- Search for not indexed models
- Lint errors


### [0.1.0] - 30-05-2019
#### Added
- Global search
- Add filters to model list page
- Set default form layouts for fields

#### Changed
- Search for not indexed models

#### Fixed
- Make datepicker work with locale input format
- On menu hover resize header 
- Keep menu state after page refresh
- Search for not indexed models