# Build instructions are in setup.py

# Until https://bitbucket.org/bjones/documentation/issue/29/use-tags
# gets fixed, we can get the version number from CodeChat/__init__.py

%global checkout 79a4c43cb856

Name:           python-codechat
Version:        0.0.16
Release:        0.1.20150206hg%{checkout}%{?dist}
Summary:        A programmer's word processor
Group:          Development/Libraries
BuildArch:      noarch

License:        GPLv3+
URL:            https://bitbucket.org/bjones/documentation/

Source0:        https://bitbucket.org/bjones/documentation/get/%{checkout}.zip#/bjones-documentation-%{checkout}.zip
Patch0:         %{name}.offline_setuptools.patch

BuildRequires:  python2-devel >= 2.7
BuildRequires:  python-docutils >= 0.12
BuildRequires:  python-setuptools
Requires:       python-docutils >= 0.12


%description
Welcome to CodeChat, a programmer's word processor. CodeChat encourages
literate programming by transforming source files into web pages and by
providing a powerful editor which synchronizes between the source code view
and the web view of a document. CodeChat transforms plain-text source code
into a beautiful and descriptive document, allowing you to record your ideas,
helpful hyperlinks to on-line resources, include expressive images and
diagrams, and much more.


%prep
%setup0 -n bjones-documentation-%{checkout}
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
