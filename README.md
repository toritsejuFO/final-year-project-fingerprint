# final-year-project-r305

As part of my final year graduation project; which is
**Design and Development of an Attandance Management Using Biometric Technology**.
This project implements a mini library for interacting with the adafruit r305 fingerprint
module over serial communication with upper computer.

Upper computer is raspberry pi (3) in our case, this overcomes the specific limitation of
the arduino not being able to get the template from the module character buffers or flash
library to upper computer for external storage, say a database. The library also was built
to overcome this challenge, which the arduino c++ library didn't take care of. So, rather
than modify the arduino library, why not build our python library then we said. Acknowledgement
to the [finger_sphinx](https://fingerprint-module-r305-python-and-mysql.readthedocs.io/) project,
which served as a great inspiration for the library.

And it also implements a few modules that fit our (myself, [iotstudent](https://github.com/iotstudent)
and [Ade-Joshe](https://github.com/Ade=Joshe)) project needs, which is fingerprint enrollment and
verification for lecture and exam attendance.

The library part we built in this project was further developed by us and we released it as an official
python package (library) on pypi [here](https://pypi.org/project/adafruit-fingerprint/). Documentation
is on readthedocs [here](https://adafruit-fingerprint.readthedocs.io), and github repo
[here](https://github.com/cerebrohivetech/adafruit-fingerprint). Best to visit any of the links
(documentation recommended) to better understand this project and how it works.

Maybe later, if (or when) the project gets adopted by the school (FUTO) or any other school, we'll
update the project to *pip install adafruit-fingerprint* and use the updated library instead and
make the project standard for commercial use. As at project defense, this worked very well for us
as we were under pressure and also working on other parts of the project,
[backend](https://github.com/toritsejuFO/final-year-project-backend-api) and
[frontend](https://github.com/Ade-Joshe/final-year-project). We did implement the key feature.
