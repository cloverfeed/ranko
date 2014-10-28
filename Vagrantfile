Vagrant.configure("2") do |config|
    config.vm.box = 'wheezy64'
    config.vm.box_url = 'http://vagrant.1024.lu/wheezy64.box'
    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "devops/provision.yml"
        ansible.host_key_checking = false
        ansible.groups = {
            "test" => ["default"]
        }
    end
    config.vm.network "forwarded_port", guest: 80, host: 8080
end
