import os
import shutil


def create_model(self, app, model):
    self._info("   Model   ")
    self._info("===========")

    # Open models.py to read
    with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
        self.models_file = fp

        # Check if model already exists
        for line in self.models_file.readlines():
            if 'class {0}'.format(self.model) in line:
                self._info('exists\t{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
                return

        self._info('create\t{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        # Prepare fields
        self.imports = []
        fields = []

        for field in self.fields:
            new_field = self.get_field(field)

            if new_field:
                fields.append(new_field)
                self._info('added\t{0}{1}/models.py\t{2} field'.format(
                    self.SCAFFOLD_APPS_DIR, self.app, field.split(':')[1]), 1)

    # Open models.py to append
    with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
        fp.write(''.join([import_line for import_line in self.imports]))
        fp.write(MODEL_TEMPLATE % (self.model, ''.join(field for field in fields)))




def clean_folder(app):
    for root, dirs, files in os.walk(app):

        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))

        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
