# my_services = yaml(content: inspec.profile.file('services.yml')).params
vars_json = json('/var/cache/ansible/attributes/hostvars.json')

vars = vars_json.params

control 'check-attributes-1' do
  impact 0.6
  title "Check attribtues for node: #{vars['ansible_hostname']}"
  desc '      Checking the hostvars cache is sensible  '
  describe file('/var/cache/ansible/attributes/hostvars.json') do
    it { should exist }
    #  its('mode') { should cmp 0644 }
  end
end

control 'check-vhost-ssl' do
  impact 0.6
  title "Check ssl for node: #{vars['ansible_hostname']}"
  desc '   Prevent unexpected settings.  '

  describe service(vars['apache_service']) do
    it { should be_enabled }
    it { should be_installed }
    it { should be_running }
  end

  describe port(443) do
    it { should be_listening }
  end

  url = 'https://localhost:443'

  describe http(url, ssl_verify: false) do
    its('status') { should be_in [200, 403] }
    # its('body') { should match(/This is a test page YYY/) }
    # its('headers.name') { should eq 'header' }
    its('headers.Content-Type') { should match(%r{text\/html}) }
  end

  url = 'https://mywordpresssite2.com'

  describe http(url, ssl_verify: false) do
    its('status') { should eq 200 }
    its('body') { should match(/This is a test page YYY/) }
    # its('headers.name') { should eq 'header' }
    its('headers.Content-Type') { should match(%r{text\/html}) }
  end

  describe command("echo | openssl s_client -servername mywordpresssite2.com -connect mywordpresssite2.com:443 2>/dev/null | openssl x509 -noout -subject") do
    its('stdout') { should match(/MOnkeyBadger LTd/) }
    its('exit_status') { should eq 0 }
  end

  describe command("echo | openssl s_client -servername mywordpresssite2.com -connect mywordpresssite2.com:443 2>/dev/null | openssl x509 -noout -issuer") do
    its('stdout') { should match(/MOnkeyBadger LTd/) }
    its('exit_status') { should eq 0 }
  end

  describe command("echo | openssl s_client -servername mywordpresssite2.com -connect mywordpresssite2.com:443 2>/dev/null | openssl x509 -noout -text -certopt no_subject,no_header,no_version,no_serial,no_signame,no_validity,no_issuer,no_pubkey,no_sigdump,no_aux") do
    its('stdout') { should match(/DNS:mywordpresssite2.com/) }
    its('stdout') { should match(/DNS:www.mywordpresssite2.com/) }
    its('exit_status') { should eq 0 }
  end


  url = 'https://mywordpresssite3.com'

  describe http(url, ssl_verify: false) do
    its('status') { should eq 200 }
    its('body') { should match(/This is a test page YYY/) }
    # its('headers.name') { should eq 'header' }
    its('headers.Content-Type') { should match(%r{text\/html}) }
  end

  describe command("echo | openssl s_client -servername mywordpresssite3.com -connect mywordpresssite2.com:443 2>/dev/null | openssl x509 -noout -subject") do
    its('stdout') { should match(/MOnkeyBadger LTd/) }
    its('exit_status') { should eq 0 }
  end

  describe command("echo | openssl s_client -servername mywordpresssite3.com -connect mywordpresssite2.com:443 2>/dev/null | openssl x509 -noout -issuer") do
    its('stdout') { should match(/MOnkeyBadger LTd/) }
    its('exit_status') { should eq 0 }
  end

  describe command("echo | openssl s_client -servername mywordpresssite3.com -connect mywordpresssite3.com:443 2>/dev/null | openssl x509 -noout -text -certopt no_subject,no_header,no_version,no_serial,no_signame,no_validity,no_issuer,no_pubkey,no_sigdump,no_aux") do
    its('stdout') { should match(/DNS:mywordpresssite3.com/) }
    its('stdout') { should match(/DNS:www.mywordpresssite3.com/) }
    its('exit_status') { should eq 0 }
  end

end
