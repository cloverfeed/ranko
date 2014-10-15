Vagrant.configure("2") do |config|
    config.vm.box = "debian80"
    config.vm.box_url = "https://downloads.sourceforge.net/project/vagrantboxjessie/debian80.box"
    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "devops/provision.yml"
        ansible.host_key_checking = false
    end
    config.vm.network "forwarded_port", guest: 80, host: 8080
end
