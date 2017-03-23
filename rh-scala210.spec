%{!?scl_name_base:%global scl_name_base rh-scala}
%{!?scl_name_version:%global scl_name_version 210}
%{!?scl:%global scl %{scl_name_base}%{scl_name_version}}
%scl_package %scl
%global scl_java_common rh-java-common

%global debug_package %{nil}

Name:       %scl_name
Version:    1
Release:    2%{?dist}
Summary:    Package that installs %scl

License:    GPLv2+
#URL:
Source1:    macros.%{scl_name}
Source2:    javapackages-config.json
Source3:    xmvn-configuration.xml
Source4:    README
Source5:    LICENSE

BuildRequires:  help2man
BuildRequires:  scl-utils-build
BuildRequires:  %{scl_java_common}-javapackages-tools

Requires:         %{name}-runtime = %{version}-%{release}
Requires:         %{scl_name}-scala

%description
This is the main package for the %scl Software Collection.

%package runtime
Summary:    Package that handles %scl Software Collection.
Requires:   scl-utils
Requires:   java-openjdk-headless >= 1:1.7

%description runtime
Package shipping essential scripts to work with the %scl Software Collection.

%package build
Summary:    Build support tools for the %scl Software Collection.
Requires:   scl-utils-build
Requires:   %{name}-scldevel = %{version}-%{release}

%description build
Package shipping essential configuration marcros/files in order to be able
to build %scl Software Collection.

%package scldevel
Summary:    Package shipping development files for %scl
Requires:   %{name}-runtime = %{version}-%{release}
Requires:   java-devel-openjdk >= 1:1.7

%description scldevel
Package shipping development files, especially useful for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T
#===================#
# SCL enable script #
#===================#
cat <<EOF >enable
. /opt/rh/%{scl_java_common}/enable

# Generic variables
export PATH="%{_bindir}:\${PATH:-/bin:/usr/bin}"
export MANPATH="%{_mandir}\${MANPATH:+:}\${MANPATH:-}"
export PYTHONPATH="%{_scl_root}%{python_sitelib}\${PYTHONPATH:+:}\${PYTHONPATH:-}"

export JAVACONFDIRS="%{_sysconfdir}/java\${JAVACONFDIRS:+:}\${JAVACONFDIRS:-}"
export XDG_CONFIG_DIRS="%{_sysconfdir}/xdg:\${XDG_CONFIG_DIRS:-/etc/xdg}"
export XDG_DATA_DIRS="%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
EOF

# Generate java.conf
cat <<EOF >java.conf
JAVA_LIBDIR=/opt/rh/%{scl_name}/root/usr/share/java
JNI_LIBDIR=/opt/rh/%{scl_name}/root/usr/lib/java
JVM_ROOT=/opt/rh/%{scl_name}/root/usr/lib/jvm
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE4})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE5} .

cp %{SOURCE1} macros.%{scl_name}
cat >> macros.%{scl_name} << EOF
%%_sysconfdir_scala %_sysconfdir
%%_prefix_scala %_prefix
%%_exec_prefix_scala %_exec_prefix
%%_bindir_scala %_bindir
%%_libdir_scala %_libdir
%%_libexecdir_scala %_libexecdir
%%_sbindir_scala %_sbindir
%%_sharedstatedir_scala %_sharedstatedir
%%_datarootdir_scala %_datarootdir
%%_datadir_scala %_datadir
%%_includedir_scala %_includedir
%%_infodir_scala %_infodir
%%_mandir_scala %_mandir
%%_localstatedir_scala %_localstatedir
%%_initddir_scala %_initddir
%%_javadir_scala %_javadir
%%_jnidir_scala %_jnidir
%%_javadocdir_scala %_javadocdir
%%_mavenpomdir_scala %_mavenpomdir
%%_jvmdir_scala %_jvmdir
%%_jvmsysconfdir_scala %_jvmsysconfdir
%%_jvmcommonsysconfdir_scala %_jvmcommonsysconfdir
%%_jvmjardir_scala %_jvmjardir
%%_jvmprivdir_scala %_jvmprivdir
%%_jvmlibdir_scala %_jvmlibdir
%%_jvmdatadir_scala %_jvmdatadir
%%_jvmcommonlibdir_scala %_jvmcommonlibdir
%%_jvmcommondatadir_scala %_jvmcommondatadir
%%_javaconfdir_scala %_javaconfdir
EOF

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7
# Fix single quotes in man page.
sed -i "s/'/\\\\(aq/g" %{scl_name}.7

%install
# Parentheses are needed here as workaround for rhbz#1017085
(%scl_install)

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 enable %{buildroot}%{_scl_scripts}/

# install rpm magic
install -Dpm0644 macros.%{scl_name} %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

# install dirs used by some deps
install -dm0755 %{buildroot}%{_prefix}/lib/rpm
install -dm0755 %{buildroot}%{_scl_root}%{python_sitelib}

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

# java.conf, javapackages-config.json and XMvn config
install -m 755 -d %{buildroot}%{_javaconfdir}
install -m 644 -p %{SOURCE2} %{buildroot}%{_javaconfdir}/
install -m 644 -p java.conf %{buildroot}%{_javaconfdir}/
install -m 755 -d %{buildroot}%{_sysconfdir}/xdg/xmvn
install -m 644 -p %{SOURCE3} %{buildroot}%{_sysconfdir}/xdg/xmvn/configuration.xml

install -m 755 -d %{buildroot}%{_jnidir}
install -m 755 -d %{buildroot}%{_javadir}
install -m 755 -d %{buildroot}%{_javadocdir}
install -m 755 -d %{buildroot}%{_mandir}/man1
install -m 755 -d %{buildroot}%{_mandir}/man7
install -m 755 -d %{buildroot}%{_datadir}/maven-metadata
install -m 755 -d %{buildroot}%{_mavenpomdir}
install -m 755 -d %{buildroot}%{_datadir}/xmvn
install -m 755 -d %{buildroot}%{_datadir}/licenses

# Empty package (no file content).  The sole purpose of this package
# is collecting its dependencies so that the whole SCL can be
# installed by installing %{name}.
%files

%files runtime
%doc README LICENSE
%{scl_files}
%{_prefix}/lib/python2.*
%{_prefix}/lib/rpm
%{_mandir}/man7/%{scl_name}.*
%{_javaconfdir}/
%dir %{_jnidir}
%dir %{_javadir}
%dir %{_javadocdir}
%dir %{_mandir}/man1
%dir %{_mandir}/man7
%dir %{_datadir}/maven-metadata
%dir %{_mavenpomdir}
%dir %{_datadir}/xmvn
%dir %{_datadir}/licenses

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Mon Jan  9 2017 Mikolaj Izdebski <mizdebsk@redhat.com> - 1-2
- Add requires on OpenJDK
- Update README

* Thu Jan  5 2017 Mikolaj Izdebski <mizdebsk@redhat.com> - 1-1
- Initial packaging
