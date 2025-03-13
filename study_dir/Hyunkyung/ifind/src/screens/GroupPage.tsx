import AsyncStorage from "@react-native-async-storage/async-storage";
import firestore from '@react-native-firebase/firestore';
import messaging from '@react-native-firebase/messaging';
import storage from '@react-native-firebase/storage';
import { useIsFocused } from "@react-navigation/native";
import React, { useEffect, useState } from "react";
import { Alert, Button, FlatList, Image, Modal, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import ImagePicker from 'react-native-image-crop-picker';
import { SafeAreaProvider } from "react-native-safe-area-context";
import theme from "../styles/theme";

interface Group {
    name: string;
    members: string;
    img_url?: string;
}

interface Member {
    uid: string;
    name: string;
}

interface SelectedImage {
    image: {
        path: string;
        filename: string;
        mime: string;
        exif?: any;
    };
    groupName: string;
}

const defaultIcon = require('../asset/cuby.png');

export const GroupPage = () => {

    const [groups, setGroups] = useState<Group[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [modalVisible, setModalVisible] = useState(false);
    const [selectedImage, setSelectedImage] = useState<SelectedImage | null>(null);
    const isFocused = useIsFocused();

    useEffect(() => {
        if (isFocused) {
            fetchGroups();
        }
    }, [isFocused]);

    //url 여부 확인
    useEffect(() => {
        console.log(groups.map(group => group.img_url));
    }, [groups]);

    //그룹에서 이미지 업데이트하면 바로 변경처리
    useEffect(() => {
        const unsubscribe = firestore()
            .collection('group')
            .onSnapshot(snapshot => {
                const updatedGroups = snapshot.docs.map(doc => {
                    const data = doc.data();
                    return {
                        id: doc.id,
                        name: data.name,
                        members: data.members,
                        img_url: data.img_url
                    };
                });
                setGroups(updatedGroups);
            });
    
        return () => unsubscribe();
    }, []);

    //앱 시작할 때 알람 권한 요청하기
    async function requestUserPermission() {
        const authStatus = await messaging().requestPermission();
        const enabled =
            authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
            authStatus === messaging.AuthorizationStatus.PROVISIONAL;
    
        if (enabled) {
            console.log('권한 상태:', authStatus);
            getTokenAndSave();
        }
    }
    
    //알림 권한 받으면 FCM토큰 users-uid에 저장
    async function getTokenAndSave() {
        const token = await messaging().getToken();
        const uid = await AsyncStorage.getItem('userUID');
        if (uid) {
            firestore()
                .collection('users')
                .doc(uid)
                .update({ fcmToken: token })
                .then(() => console.log('Token saved to Firestore'))
                .catch((error) => console.error('토큰 저장 오류:', error));
        }
    }
    useEffect(() => {
        requestUserPermission();
    }, []);

    const fetchGroups = async () => {
        const uid = await AsyncStorage.getItem('userUID');
        if (uid) {
            const userDoc = await firestore().collection('users').doc(uid).get();
            if (userDoc.exists) {
                const userData = userDoc.data();
                if (userData && userData.groups) {
                    const userGroups = userData.groups;
                    const groupsData = await Promise.all(userGroups.map(async (groupName:string) => {
                        const groupDoc = await firestore().collection('group').doc(groupName).get();
                        if (groupDoc.exists) {
                            const groupData = groupDoc.data();
                            if (groupData) { // 배열 여부 확인
                                return {
                                    name: groupName,
                                    // members: groupData.members.map(member => member.name).join(', '), //멤버 목록
                                    img_url: groupData.img_url
                                };
                            }
                        }
                        return { name: groupName, img_url: undefined };  // 오류 상황 처리
                    }));
                    setGroups(groupsData);
                } else {
                    setGroups([]);
                }
            }
        }
        setLoading(false);
    };
    


    useEffect(() => {
        fetchGroups();
    }, []);

    const leaveGroup = async (groupName: string) => {
        const uid = await AsyncStorage.getItem('userUID');
        if (uid) {
            const groupDoc = await firestore().collection('group').doc(groupName).get();
            if (groupDoc.exists) {
                const groupData = groupDoc.data();
                if (groupData && groupData.members) {
                    const memberInfo = groupData.members.find((member: Member) => member.uid === uid);
                    if (memberInfo) {
                        await firestore().collection('group').doc(groupName).update({
                            members: firestore.FieldValue.arrayRemove(memberInfo)
                        });
                        console.log("User removed from the group");
                    }
                }
            }
    
            await firestore().collection('users').doc(uid).update({
                groups: firestore.FieldValue.arrayRemove(groupName)
            });
            
            fetchGroups();
            Alert.alert("그룹에서 나갔습니다.", `${groupName} 그룹을 떠났습니다.`);
        }
    };

    // 이미지 업로드 확인 모달 표시
    const handleImageSelection = async (groupName: string) => {
        try {
            const image = await ImagePicker.openPicker({
                width: 300,
                height: 400,
                cropping: false,
                includeBase64: false,
                includeExif: true,
            });

            console.log('선택한 이미지의 메타데이터:', image.exif);  // 메타데이터 로그 출력
            const safeFilename = image.filename || `none-${Date.now()}`;
    
            setSelectedImage({
                image: {
                    path: image.path,
                    filename: safeFilename,
                    mime: image.mime,
                },
                groupName
            });
            setModalVisible(true);
        } catch (error) {
            console.log('이미지 선택 오류:', error);
        }
    };

    const uploadSelectedImage = async () => {
        if (!selectedImage) return;
        const { image, groupName } = selectedImage;
        const { path, filename, mime, exif } = image;
        const storageRef = storage().ref(`images/${groupName}/${filename}`);
        
        // 여기에서 메타데이터를 설정합니다.
        const metadata = {
            contentType: mime,
            customMetadata: {
                'exif': JSON.stringify(exif) // JSON 문자열로 변환하여 EXIF 데이터를 저장
            }
        };
    
        const uploadTask = storageRef.putFile(path, metadata);
    
        uploadTask.on('state_changed',
            (snapshot) => {
                const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
                console.log('업로드 진행 상태: ' + progress + '% 완료');
            },
            (error) => {
                console.error('업로드 오류:', error);
            },
            async () => {
                const downloadURL = await uploadTask.snapshot?.ref.getDownloadURL();
                if (downloadURL) {
                    await firestore().collection('group').doc(groupName).update({ img_url: downloadURL });
                    const updatedGroups = groups.map(group =>
                        group.name === groupName ? { ...group, img_url: downloadURL } : group
                    );
                    setGroups(updatedGroups);
                    Alert.alert("업로드 완료", "이미지가 성공적으로 공유되었습니다.");
                } else {
                    console.error('Failed to get download URL');
                    Alert.alert("공유 실패", "이미지 공유를 실패했습니다.");
                }
            }
        );
        setModalVisible(false);
    };
    
    
    const isValidUrl = (url:string) => {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    };

    return (
        <SafeAreaProvider>
            <View style={styles.container}>
                <Text style={styles.title}>그룹 사진 공유하기</Text>
                <View style={styles.separator} />
                <Modal
    animationType="slide"
    transparent={true}
    visible={modalVisible}
    onRequestClose={() => {
        Alert.alert("모달이 닫힙니다.");
        setModalVisible(!modalVisible);
    }}
>
    <View style={styles.centeredView}>
        <View style={styles.modalView}>
            <Image
                source={selectedImage ? { uri: selectedImage.image.path } : undefined}
                style={styles.previewImage}
                resizeMode="contain"
            />
            <Text style={styles.modalText}>이 이미지를 업로드하시겠습니까?</Text>
            <View style={styles.horizontalButtons}>
                <Button title="예" onPress={uploadSelectedImage} />
                <Button title="아니오" onPress={() => setModalVisible(false)} />
            </View>
        </View>
    </View>
</Modal>
                {loading ? (
                    <Text>Loading groups...</Text>
                ) : (
                    groups.length > 0 ? (
                        <FlatList<Group>
                            data={groups}
                            keyExtractor={(item) => item.name}
                            renderItem={({ item }) => (
                                <View style={styles.groupItem}>
                                    <Image
                                    source={item.img_url && isValidUrl(item.img_url) ? { uri: item.img_url } : defaultIcon}
                                    style={styles.groupImage}
                                    resizeMode="cover"
                                    />
                                    <View style={styles.groupInfo}>
                                    <Text style={styles.groupName}>{item.name}</Text>
                                    {/* <Text style={styles.groupMember}>{item.members}</Text> */}
                                    </View>
                                    <TouchableOpacity style={styles.uploadButton} onPress={() => handleImageSelection(item.name)}>
                                        <Text style={styles.leaveButtonText}>업로드</Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity style={styles.leaveButton} onPress={() => leaveGroup(item.name)}>
                                        <Text style={styles.leaveButtonText}>나가기</Text>
                                    </TouchableOpacity>
                                </View>
                            )}
                        />
                    ) : (
                        <Text>가입 된 그룹이 없습니다.</Text>
                    )
                )}
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
    title: {
        paddingTop: 10,
        margin: 10,
        fontSize: 35,
        // fontWeight: "bold",
        fontFamily: theme.mainfont,
        color: theme.mainDarkGrey,
    },
    separator: {
        width: '90%',
        height: 1,
        backgroundColor: theme.navicolor,
        marginBottom: 10,
    },
    groupItem: {
        flexDirection: 'row',
        padding: 10,
        marginBottom: 10,
        // alignItems: 'center',
        backgroundColor: theme.mainOrange,
        borderRadius: 20,
    },
    groupImage: {
        width: 100,
        height: 100,
        borderRadius: 10,
        marginRight: 5,
    },
    groupInfo: {
        marginRight: '10%',
    },
    groupName: {
        fontSize: 25,
        // fontWeight: 'bold',
        color: theme.mainDarkGrey,
        fontFamily: theme.mainfont,
        paddingBottom: 10,
    },
    groupMember: {
        fontSize: 17,
        color: 'gray',
        fontFamily: theme.mainfont,
    },
    uploadButton: {
        padding: 10,
        backgroundColor: theme.lineblue,
        borderRadius: 20,
        // marginLeft: '10%',
    },
    leaveButton: {
        padding: 10,
        backgroundColor: theme.mainRed,
        borderRadius: 20,
        marginLeft: 5,
    },
    leaveButtonText: {
        marginTop: 10,
        color: 'white',
        fontSize: 16,
        fontFamily: theme.mainfont,
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
            height: 2
        },
        shadowOpacity: 0.25,
        shadowRadius: 4,
        elevation: 5
    },
    previewImage: {
        width: 200,
        height: 200,
        marginBottom: 15,
    },
    modalText: {
        marginBottom: 15,
        textAlign: "center"
    },
    horizontalButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '60%',
    }
});