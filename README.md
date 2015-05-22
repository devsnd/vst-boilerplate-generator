vst-boilerplate-generator
=========================

Generates Boilerplate C++ Code for writing VSTs

vst-boilerplate-generator uses python and a template engine
to create some VST effect boilerplate code for you.

*Linux only* at the moment.

Install:
-------------------------

    git clone git@github.com:devsnd/vst-boilerplate-generator.git

Install the template engine jinja2 in a virtualenv or using a package manager
(make sure to use python 3.4):

    pip3 install jinja2

Usage:
-------------------------

First you need to create a config file for your effect, which makes it easy
to change the most important parameters of your effect:

    ./vst-boilerplate-generator.py --create-effect-config MyFunkyEffect

vst-boilerplate-generator will ask for the location of the VST SDK on first launch.

After running the `--create-effect-config` command, you can edit the configuration
file to specify the VST parameters, names, inputs, outputs and so on.

When finished editing the configuration, you can generate the boilerplate:

    ./vst-boilerplate-generator.py --create-effect MyFunkyEffect

You can then build the VST using make:

    cd vsts/MyFunkyEffect
    make

which will create a `MyFunkyEffect.so` file.


Source:
-------------------------

Copyright (c) 2015 Tom Wallroth

Sources on github:
  http://github.com/devsnd/vst-boilerplate-generator/

licensed under GNU GPL version 3 (or later)