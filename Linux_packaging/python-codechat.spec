# .. Copyright (C) 2012-2015 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# .. highlight:: spec
#
# ************************************************************
# python-codechat.spec - openSUSE Build Service packaging file
# ************************************************************
# This was created by Yajo.
#
# Build instructions are in setup.py
Name:           python-codechat
Version:        1.2.1
Release:        %{version}%{?dist}
Summary:        A programmer's word processor
Group:          Development/Libraries
BuildArch:      noarch

License:        GPLv3+
URL:            https://github.com/bjones1/CodeChat

Source0:        https://github.com/bjones1/CodeChat/archive/v%{version}.zip
Patch0:         %{name}.offline_setuptools.patch

BuildRequires:  python2-devel >= 2.7
BuildRequires:  python-docutils >= 0.12
BuildRequires:  python-setuptools
Requires:       python-docutils >= 0.12
Requires:       python-pygments >= 2.0


%description
Welcome to CodeChat, a programmer's word processor. CodeChat encourages
literate programming by transforming source files into web pages and by
providing a powerful editor which synchronizes between the source code view
and the web view of a document. CodeChat transforms plain-text source code
into a beautiful and descriptive document, allowing you to record your ideas,
helpful hyperlinks to on-line resources, include expressive images and
diagrams, and much more.


%prep
%setup0 -n v%{version}
%patch0

%build
CFLAGS="%{optflags}" %{__python} setup.py build


%install
%{__python2} setup.py install --skip-build --root %{buildroot}


%files
%doc CodeChat/LICENSE.html README.rst
%{python_sitelib}/CodeChat*


%changelog
* Fri Feb 6 2015 Jairo Llopis <yajo.sk8@gmail.com> 0.0.16-0.1.20150206hg79a4c43cb856
- First release.
