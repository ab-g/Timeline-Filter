import sys
import os
import json


def get_first_scene_id(resource_pack_data):
    return resource_pack_data['scenes']['map'][0]['value']['id']['uuid']


def get_first_state_machine_id(resource_pack_data):
    return resource_pack_data['stateMachines']['map'][0]['value']['id']['uuid']


def get_states_ids(game_project_dir_path, resource_pack_data):
    state_machine_id = get_first_state_machine_id(resource_pack_data)
    state_machine_file_path = os.path.join(game_project_dir_path, 'state-machines/{0}.json'.format(state_machine_id))

    with open(state_machine_file_path, 'r') as state_machine_file:
        state_machine_data = json.load(state_machine_file)
        return [state['id']['uuid'] for state in state_machine_data['states']]


def filter_node_children(node, safe_scripts_ids):
    if 'timeline' in node['object3D'] and node['object3D']['timeline']['timelineId']['uuid'] not in safe_scripts_ids:
        del node['object3D']['timeline']
    return node


def main(game_project_dir_path):
    resource_pack_file_path = os.path.join(game_project_dir_path, 'resource-pack.json')
    with open(resource_pack_file_path, 'r') as resource_pack_file:
        resource_pack_data = json.load(resource_pack_file)

    scene_id = get_first_scene_id(resource_pack_data)
    scene_file_path = os.path.join(game_project_dir_path, 'scenes/{0}.json'.format(scene_id))
    with open(scene_file_path, 'r') as scene_file:
        scene_data = json.load(scene_file)

    states_ids = get_states_ids(game_project_dir_path, resource_pack_data)

    safe_scripts_ids = [
        '1866A820-41DD-4A40-9561-03AF112A0633',
        '299688C6-1019-4261-97F4-2B249AECBC00',
        'E37AFDD4-8FFA-4550-BB32-40DCC78076E0'
    ]
    for script in scene_data['scriptSystem']['scripts']:
        script_id = script['id']['uuid']
        script_file_path = os.path.join(game_project_dir_path, 'scripts/{0}.json'.format(script_id))
        script_class = script['@class']
        if script_class == 'TimeLineScript':
            with open(script_file_path, 'r') as script_file:
                script_data = json.load(script_file)
                if 'triggers' in script_data and len(script_data['triggers']):
                    for trigger_data in script_data['triggers']:
                        if 'state_id' in trigger_data and trigger_data['state_id']['uuid'] in states_ids:
                            safe_scripts_ids.append(script_id)

    scene_data['scriptSystem']['scripts'] = [
        script for script in scene_data['scriptSystem']['scripts']
        if script['@class'] != 'TimeLineScript' or script['id']['uuid'] in safe_scripts_ids
    ]
    # print(json.dumps(scene_data, indent=4))
    with open(scene_file_path, 'w') as scene_file:
        json.dump(scene_data, scene_file, indent=4, sort_keys=False)

    character_id = resource_pack_data['defaultCharacterId']['uuid']
    character_file_path = os.path.join(game_project_dir_path, 'characters/{0}.json'.format(character_id))
    with open(character_file_path, 'r') as character_file:
        character_data = json.load(character_file)

    character_data['body'] = [
        filter_node_children(node, safe_scripts_ids) for node in character_data['body']
    ]
    # print(json.dumps(character_data, indent=4))
    with open(character_file_path, 'w') as character_file:
        json.dump(character_data, character_file, indent=4, sort_keys=False)


if __name__ == '__main__':
    main(sys.argv[1])

