Summary:	An NTP client/server
Name:		chrony
Version:	1.26
Release:	3
License:	GPL v2
Group:		Daemons
Source0:	http://download.tuxfamily.org/chrony/%{name}-%{version}.tar.gz
# Source0-md5:	ad6dd619ff1986e4ff780363c64e2246
Source1:	%{name}.conf
Source2:	%{name}d.service
Source3:	%{name}-wait.service
URL:		http://chrony.tuxfamily.org/
BuildRequires:	bison
BuildRequires:	libcap-devel
BuildRequires:	readline-devel
BuildRequires:	texinfo
Requires(pre,postun):	pwdutils
Provides:	group(ntp)
Provides:	ntpdaemon
Provides:	user(ntp)
Obsoletes:	ntpdaemon
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/ntp

%description
Chrony is a pair of programs which are used to maintain the accuracy
of the system clock on a computer.

%prep
%setup -q

%{__sed} -i -e 's,/usr/local,%{_prefix},g' *.texi

%build
export CC="%{__cc}"
export CFLAGS="%{rpmcflags} -Wmissing-prototypes -Wall"
export CPPFLAGS="%{rpmcppflags}"

# custom configure script used
./configure \
	--docdir=%{_docdir}		\
	--prefix=%{_prefix}		\
	--sysconfdir=%{_sysconfdir} 	\
	--without-editline

%{__make} getdate all docs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/var/{lib/ntp,log/chrony}} \
	$RPM_BUILD_ROOT%{systemdunitdir}

%{__make} install install-docs \
	DESTDIR=$RPM_BUILD_ROOT

rm -rf $RPM_BUILD_ROOT%{_docdir}

cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/chrony.conf
cp -a %{SOURCE2} %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}

touch $RPM_BUILD_ROOT%{_localstatedir}/lib/ntp/{drift,rtc}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 101 ntp
%useradd -u 101 -d %{_localstatedir}/lib/ntp -g ntp -c "NTP Daemon" ntp

%post
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1
%systemd_post chronyd.service chrony-wait.service

%preun
%systemd_preun chronyd.service chrony-wait.service

%postun
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1
%systemd_reload
if [ "$1" = "0" ]; then
	%userremove ntp
	%groupremove ntp
fi

%files
%defattr(644,root,root,755)
%doc NEWS README chrony.txt faq.txt examples/*
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/chrony.conf
%attr(755,root,root) %{_bindir}/chronyc
%attr(755,root,root) %{_sbindir}/chronyd
%{systemdunitdir}/*.service
%{_mandir}/man[1,5,8]/chrony*.*
%{_infodir}/chrony.info*

%dir %attr(770,ntp,ntp) /var/log/chrony
%dir %attr(770,root,ntp) /var/lib/ntp
%attr(640,ntp,ntp) %ghost /var/lib/ntp/drift
%attr(640,ntp,ntp) %ghost /var/lib/ntp/rtc

