import AsyncStorage from '@react-native-async-storage/async-storage';
import firestore from '@react-native-firebase/firestore';
import React, { useEffect, useState } from "react";
import { Alert, FlatList, Modal, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import theme from "../styles/theme";

interface User {
    id: string;
    phone: string;
    name: string;
}
interface Member {
    uid: string;
    name: string;
}

export const MakeGroup = () => {
    const [phoneNumber, setPhoneNumber] = useState('');
    const [users, setUsers] = useState<User[]>([]);
    const [members, setMembers] = useState<Member[]>([]);
    const [groupName, setGroupName] = useState('');
    const [modalVisible, setModalVisible] = useState(false);

    useEffect(() => {
        fetchGroupMembers();
    }, []);

    const fetchCurrentUser = async () => {
        const uid = await AsyncStorage.getItem('userUID');
        if (uid) {
            const userDoc = await firestore().collection('users').doc(uid).get();
            if (userDoc.exists) {
                const userData = userDoc.data();
                if (userData) { // userData가 실제로 존재하는지 확인
                    setMembers(prevMembers => [...prevMembers, { uid: uid, name: userData.name }]);
                } else {
                    // userData가 없는 경우의 처리 로직
                    console.log("잘못된 접근 경로입니다");
                }
            } else {
                // userDoc이 존재하지 않는 경우의 처리 로직
                console.log("잘못된 접근 경로입니다.");
            }
        } else {
            // UID를 가져오지 못한 경우의 처리 로직
            console.log("uid없음");
        }
    };

    const fetchGroupMembers = async () => {
        const doc = await firestore().collection('group').doc('temp').get();
        if (doc.exists) {
            const data = doc.data();
            if (data && data.members) {
                const membersData = data.members as Member[];
                setMembers(membersData);
            } else {
                setMembers([]);
            }
        } else {
            setMembers([]);
        }
    };

    const searchUsers = async () => {
        const querySnapshot = await firestore()
            .collection('users')
            .where('phone', '==', phoneNumber)
            .get();

        if (querySnapshot.empty) {
            Alert.alert("전화번호를 확인해주세요", "검색된 사용자가 없습니다.");
        } else {
            const usersToAdd: Member[] = querySnapshot.docs.map(doc => ({
                uid: doc.id,
                name: doc.data().name,
            }));
            addMemberToGroup(usersToAdd);
            setPhoneNumber('');
        }
    };

    const addMemberToGroup = async (newMembers: Member[]) => {
        await firestore().collection('group').doc('temp').set({
            members: firestore.FieldValue.arrayUnion(...newMembers)
        }, { merge: true });
        fetchGroupMembers();
    };

    const removeMemberFromGroup = async (uid: string) => {
        const updatedMembers = members.filter(member => member.uid !== uid);
        await firestore().collection('group').doc('temp').set({
            members: updatedMembers
        });
        fetchGroupMembers();
    };

    const finalizeGroupName = async () => {
        if (groupName.trim() === '') {
            Alert.alert("그룹 이름을 입력해주세요.");
            return;
        }

        const uid = await AsyncStorage.getItem('userUID');
        if (uid) {
            const userDoc = await firestore().collection('users').doc(uid).get();
            if (userDoc.exists) {
                const userData = userDoc.data();
                if (userData) {
                    const currentUserMember = { uid: uid, name: userData.name };
                    const updatedMembers = [...members, currentUserMember];

                    await firestore().collection('group').doc(groupName).set({
                        members: updatedMembers
                    });

                    updatedMembers.forEach(async member => {
                        await firestore().collection('users').doc(member.uid).set({
                            groups: firestore.FieldValue.arrayUnion(groupName)
                        }, { merge: true });
                    });

                    await firestore().collection('group').doc('temp').delete();
                    setModalVisible(false);
                    setMembers([]);
                    Alert.alert("그룹이 생성되었습니다!");
                } else {
                    console.log("사용자 데이터가 없습니다.");
                }
            } else {
                console.log("사용자 문서를 찾을 수 없습니다.");
            }
        } else {
            console.log("UID를 가져올 수 없습니다.");
        }
    };
    return (
        <SafeAreaProvider>
            <View style={styles.container}>
                <Text style={styles.title}>그룹 만들기</Text>
                <View style={styles.separator} />
                <View style={styles.search}>
                <View style={styles.inputContainer}>
                    <TextInput
                        style={styles.info}
                        placeholder="전화번호 입력"
                        keyboardType="phone-pad"
                        placeholderTextColor='#3e3e3e'
                        value={phoneNumber}
                        onChangeText={setPhoneNumber}
                    />
                </View>
                    <TouchableOpacity
                        style={styles.search_button}
                        onPress={searchUsers}
                    >
                        <Text style={styles.buttonText}>확인</Text>
                    </TouchableOpacity>
                    </View>
                    <FlatList
                    data={members}
                    keyExtractor={item => item.uid}
                    renderItem={({ item }) => (
                        <View style={styles.listItem}>
                            <Text style={styles.listItemText}>{item.name}</Text>
                            <TouchableOpacity style={styles.deleteButton} onPress={() => removeMemberFromGroup(item.uid)}>
                                <Text style={styles.deleteButtonText}>삭제</Text>
                            </TouchableOpacity>
                        </View>
                    )}
                />
            <TouchableOpacity
                    style={styles.submitButton}
                    onPress={() => setModalVisible(true)}
                >
                    <Text style={styles.buttonText}>선택 완료</Text>
                </TouchableOpacity>
                <Modal
                    animationType="slide"
                    transparent={true}
                    visible={modalVisible}
                    onRequestClose={() => {
                        setModalVisible(!modalVisible);
                    }}
                >
                    <View style={styles.centeredView}>
                        <View style={styles.modalView}>
                            <TextInput
                                style={styles.info}
                                placeholder="새 그룹 이름 입력"
                                onChangeText={setGroupName}
                                placeholderTextColor='#3e3e3e'
                                value={groupName}
                            />
                            <View style={styles.buttons}>
                            <TouchableOpacity
                            style={styles.saveButton}
                            onPress={finalizeGroupName}
                            >
                            <Text style={styles.textStyle}>저장</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                            style={styles.cancelButton}
                            onPress={() => setModalVisible(false)}
                            >
                            <Text style={styles.textStyle}>취소</Text>
                        </TouchableOpacity>
                        </View>
                        </View>
                    </View>
                </Modal>
            </View>
        </SafeAreaProvider>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        backgroundColor: '#fff',
    },
    title:{
        paddingTop: 10,
        margin: 10,
        fontSize: 35,
        fontFamily: theme.mainfont,
        // fontWeight: "bold",
        color: theme.mainDarkGrey,
    },
    separator: {
        width: '90%',
        height: 1,
        backgroundColor: theme.navicolor,
        marginBottom: 5,
    },
    search: {
        marginTop: 20,
        marginBottom: 20,
        flexDirection: 'row',
        justifyContent: 'space-around',
        width: '95%',
    },
    inputContainer: {
        alignItems: 'center',
        borderWidth: 3,
        borderColor: theme.signupandin,
        borderRadius: 40,
        marginBottom: 10,
        paddingHorizontal: 10,
        paddingVertical: 5,
        width: '70%',
        color: theme.mainDarkGrey,
    },
    info: {
        fontSize: 22,
        fontFamily: theme.mainfont,
        color: theme.mainDarkGrey,
    },
    search_button: {
        backgroundColor: theme.signupandin,
        height: '90%',
        paddingTop: 20,
        paddingLeft: 10,
        paddingRight: 10,
        borderRadius: 40,
    },
    buttonText: {
        padding: 5,
        color: 'black',
        fontSize: 22,
        fontFamily: theme.mainfont,
    },
    listItem: {
        width: "90%",
        flexDirection: 'row',
        padding: 10,
        marginBottom: 20,
        borderBottomWidth: 0.5,
        borderColor: 'gray',
    },
    listItemText: {
        fontSize: 23,
        color: 'black',
        fontFamily: theme.mainfont,
        marginRight: '30%',
    },
    deleteButton: {
        backgroundColor: 'red',
        marginLeft: '40%',
        paddingBottom: 6,
        paddingTop: 6,
        paddingRight: 5,
        paddingLeft: 5,
        borderRadius: 20,
    },
    deleteButtonText: {
        color: 'white',
        fontSize: 20,
        fontFamily: theme.mainfont,
    },
    submitButton: {
        backgroundColor: theme.mainOrange,
        width: '30%',
        padding: 10,
        borderRadius: 40,
        position: 'absolute',
        bottom: 20,
        alignItems: 'center',
    },
    centeredView: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 22,
    },
    modalView: {
        margin: 20,
        backgroundColor: 'white',
        borderRadius: 20,
        padding: 35,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.25,
        shadowRadius: 4,
        elevation: 5,
    },
    modalText: {
        marginBottom: 15,
        textAlign: 'center',
        fontSize: 18,
        width: 250,
    },
    buttons: {
        flexDirection: 'row',
    },
    textStyle: {
        color: 'white',
        fontSize: 22,
        fontFamily: theme.mainfont,
        textAlign: 'center',
    },
    saveButton: {
        backgroundColor: theme.lineblue,
        padding: 10,
        borderRadius: 40,
        marginRight: 10,
    },
    cancelButton: {
        backgroundColor: theme.mainRed,
        padding: 10,
        borderRadius: 40,
        marginLeft: 10,
    }
});

