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

  url = 'https://localhost:443'
  
  describe http(url, ssl_verify: false) do
    its('status') { should eq 200 }
    its('body') { should match(/This is a test page YYY/) }
    # its('headers.name') { should eq 'header' }
    its('headers.Content-Type') { should match(%r{text\/html}) }
  end

  # describe command("echo | openssl s_client -servername #{vars['certbot_test_domain']} -connect #{vars['certbot_test_domain']}:443 2>/dev/null | openssl x509 -noout -subject") do
  #   its('stdout') { should match(/#{vars['certbot_test_domain']}/) }
  #   its('exit_status') { should eq 0 }
  # end

  # describe apache do
  #   its('user') { should eq vars['apache_user'] }
  # end

  # describe package('php') do
  #   it { should_not be_installed }
  # end

  describe port(443) do
    it { should be_listening }
  end

  describe file('/tmp') do
    it { should be_directory }
  end

  # describe file('hello.txt') do
  #   its('content') { should match 'Hello World' }
  # end
end
